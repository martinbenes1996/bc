

"""
File:           views.py
Author:         Martin Benes
Institution:    Faculty of Information Technology
                Brno University of Technology

This module contains main block entities for GUI of the app.
Developed as a part of bachelor thesis "Counting of people using PIR sensor".
"""

import logging
import os
import re

import numpy as np
import tkinter as tk

from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg)
from matplotlib.figure import Figure
from matplotlib.backend_bases import key_press_handler
import matplotlib.pyplot as plt

import comm_serial
import conf
import ui

class SerialView:
    log = logging.getLogger(__name__)
    def __init__(self, root):
        self.root = root
        self.buttons = {}

    def begin(self, create, close):
        # look up serials
        allfiles = re.findall(r'ttyS[0-9]+', ",".join(os.listdir("/dev/")))
        # sort serial files by numeric appendix numerically
        serialfiles = sorted(allfiles, key=self.sortByNumericAppendix)
        # headline
        tk.Label(self.root, text=u"Ports", font=30).grid(column=0, sticky=tk.W+tk.S, padx=30)

        # generate checkbutons
        for f in serialfiles:
            serialname = "S:/dev/" + f
            checkbutton = ui.CheckButton(self.root, serialname)
            checkbutton.checked, checkbutton.unchecked = create, close
            checkbutton.alive = comm_serial.Reader.getReader
            checkbutton.button.grid(column=0, sticky=tk.W+tk.S, padx=30)
            checkbutton.run()
            self.buttons[serialname] = checkbutton
    
    def disable(self):
        for _,chb in self.buttons.items():
            chb.disable()
    def update(self):
        for _,chb in self.buttons.items():
            chb.manualUpdate()
        self.log.debug("update serial view")

    def uncheck(self, name):
        try:
            self.buttons[name].off()
        except KeyError:
            pass
        

    @staticmethod
    def sortByNumericAppendix(name):
        """ Separates a numeric appendix from Linux serial ports name. 
        
        Keyword arguments:
            name        Serial port name.
        """
        # regex out the number
        try:
            n = re.search(r'(?<=ttyS)[0-9]+', name)
        except:
            print("Error: sortByNumericAppendix(", name, ")")
            return 0
        # convert to int
        return int( n.group(0) )

class MulticastView:
    def __init__(self, root):
        self.root = root
        self.buttons = {}
    
    def begin(self, create, close):
        tk.Label(self.root, text=u"Multicast channel", font=30).grid(column=0, sticky=tk.W+tk.N, padx=30)
        btnname = "M:"+str(conf.Config.channel())
        checkbutton_mcast = ui.CheckButton(self.root, btnname)
        checkbutton_mcast.checked, checkbutton_mcast.unchecked = create, close
        checkbutton_mcast.button.grid(column=0, sticky=tk.W+tk.N, padx=30)
        checkbutton_mcast.run()
        self.buttons[btnname] = checkbutton_mcast
    
    def uncheck(self, name):
        try:
            self.buttons[name].off()
        except KeyError:
            pass



class SignalView:
    """View of signal on serial port.
    
    Attributes:
        master  Item to show in.
        fig     MatPlotLib figure.
        subplt  Subplot to plot in.
        canvas  Connection of TKinter and MatPlotLib.
        getData Callback for getting data.
        record  Callback to control recording.
        afterId TKinter ID of planned call.
    """

    log = logging.getLogger(__name__)
    def __init__(self, root, master, reader, recorder):
        """Constructs object.
        
        Arguments:
            root        Root of view.
            master      Item to show in.
            reader      Callback for getting data.
            recorder    Callback to control recording.
        """
        # create variables
        self.master = master
        self.getData = reader
        self.record = recorder
        self.afterId = None

        # initiate MatPlotLib view
        self.fig = Figure(figsize=(6,4), dpi=100)
        self.subplt = self.fig.add_subplot(111)
        self.subplt.set_xlabel("Samples")
        self.subplt.set_ylabel("Signal value")
        self.subplt.set_ylim(0, 1027)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.master)
        self.canvas.draw()
        # set border
        self.canvas.get_tk_widget().config(highlightcolor='black', highlightbackground='black', highlightthickness=3, bd=0)

        # set mouse handlers
        self.canvas.get_tk_widget().bind('<ButtonRelease-1>', self.manualUpdate)
        self.canvas.get_tk_widget().bind('<ButtonRelease-3>', self.showMenu)
        # create right-click menu
        self.menu = RightMenu(self.master, self.manualUpdate, self.recordMenuHandler)

        # run update in separate thread
        self.update()
    
    def __del__(self):
        """Destructs object."""
        if self.afterId:
            self.master.after_cancel(self.afterId)
    
    def show(self, data):
        """Actualizes view with new data.
        
        Arguments:
            data    New data to show.
        """
        # clear view
        self.subplt.cla()
        # set view
        self.subplt.set_xlabel("Samples")
        self.subplt.set_ylabel("Signal value")
        self.subplt.set_ylim(0, 1027)
        # plot data
        self.subplt.plot(data, color='magenta')
        # paint
        self.canvas.draw()
        self.canvas.flush_events()
        #print("SignalView: update")
        
    def update(self):
        """Updates view. Runs in separated thread."""
        # show new data
        self.show( self.getData() )
        # plan next update after 300 ms
        self.afterId = self.master.after(conf.Config.period(), self.update)
        self.log.debug("update signal view")

    def manualUpdate(self, event):
        """Updates view. Handler for mouse events.
        
        Arguments:
            event       Event descriptor.
        """
        # cancel updater thread
        if self.afterId:
            self.master.after_cancel(self.afterId)
        # run new thread
        self.update()
    
    def showMenu(self, event):
        """Shows menu. Handler for mouse event.
        
        Arguments:
            event       Event descriptor.
        """
        self.menu.show(event.x_root, event.y_root)
        
    def recordMenuHandler(self, filename, status):
        """Catches event from menu to recorder to indicate to user.
        
        Arguments:
            filename    Filename to save recording to.
            status      True if turning recording on. False if turning off.
        """
        # indicate recording
        if status:
            self.canvas.get_tk_widget().config(highlightcolor='red', highlightbackground='red')
        else:
            self.canvas.get_tk_widget().config(highlightcolor='black', highlightbackground='black')
        # reemit signal
        self.record(filename)


class AreaView:
    """View of signal on serial port.
    
    Attributes:
        master  Item to show in.
        fig     MatPlotLib figure.
        subplt  Subplot to plot in.
        canvas  Connection of TKinter and MatPlotLib.
        getData Callback for getting data.
        record  Callback to control recording.
        afterId TKinter ID of planned call.
    """
    log = logging.getLogger(__name__)
    
    def __init__(self, master=None, reader=lambda:np.array([[0,0],[0,0]])):
        """Constructs object.
        
        Arguments:
            master      Item to show in.
            reader      Callback for getting data.
            recorder    Callback to control recording.
        """
        # create variables
        self.master = master
        if master == None:
            self.master = tk.Frame()
        self.reader = reader
        self.afterId = None

        # initiate MatPlotLib view
        self.fig = Figure(figsize=(6,4))
        self.subplt = self.fig.add_subplot(111)
        self.subplt.set_xlabel("Orientation")
        self.subplt.set_ylabel("Distance")
        self.subplt.set_ylim(0, 12)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.master)
        self.canvas.draw()
        self.y,self.x = np.mgrid[slice(0,13,6),slice(0,13,6)]
        # set border
        self.canvas.get_tk_widget().config(highlightcolor='black', highlightbackground='black', highlightthickness=3, bd=0)

        # set mouse handlers
        self.canvas.get_tk_widget().bind('<ButtonRelease-1>', self.manualUpdate)
        #self.canvas.get_tk_widget().bind('<ButtonRelease-3>', self.showMenu)
        # create right-click menu
        #self.menu = RightMenu(self.master, self.manualUpdate, self.recordMenuHandler)

        # run update in separate thread
        self.update()
    
    def __del__(self):
        """Destructs object."""
        if self.afterId:
            self.master.after_cancel(self.afterId)
    
    def show(self, data):
        """Actualizes view with new data.
        
        Arguments:
            data    New data to show.
        """
        print(data)
        # clear view
        self.subplt.cla()
        # set view
        self.subplt.set_xlabel("Orientation")
        self.subplt.set_ylabel("Distance")
        self.subplt.set_ylim(0, 12)
        # plot data
        self.subplt.pcolormesh(self.x, self.y, data, vmin=0, vmax=1, cmap='hot')
        # paint
        self.canvas.draw()
        self.canvas.flush_events()
        
    def update(self):
        """Updates view. Runs in separated thread."""
        # show new data
        self.show( self.reader() )
        # plan next update after 300 ms
        self.afterId = self.master.after(conf.Config.period(), self.update)
        self.log.debug("update area view")

    def manualUpdate(self, event):
        """Updates view. Handler for mouse events.
        
        Arguments:
            event       Event descriptor.
        """
        # cancel updater thread
        if self.afterId:
            self.master.after_cancel(self.afterId)
        # run new thread
        self.update()

class ReplayView:
    """Replay controller.
    
    Attributes:
        master  Item to show in.
    """
    log = logging.getLogger(__name__)
    def __init__(self, master=None, replay=lambda:None):
        self.master = master
        self.frame = tk.Frame(master)
        self.replay = replay
        self.replayBtn = tk.Button(self.frame, text="Replay", command=self.restart)
        self.replayBtn.grid(sticky=tk.N)
    
    def restart(self):
        self.log.debug("restart replaying with "+str(self.replay))
        self.replay()


        
class RightMenu:
    """Menu after right-click on view.
    
    Attributes:
        record      Callback to control recording.
        recording   Recording status.
        popup       Menu object.
    """
    def __init__(self, master, refresh, record):
        """Constructs objects.
        
        Arguments:
            master      Item to show in.
            refresh     Callback for refreshing.
            record      Callback to control recording.
        """
        # create variables
        self.record = record
        self.recording = False
        # generate menu
        self.popup = tk.Menu(master, tearoff=0)
        self.popup.add_command(label="Refresh", command=refresh)
        self.popup.add_command(label="Pause", command=self.pause)
        self.popup.add_command(label="Record", command=self.switchRecord)

    def pause(self):
        """Pauses updating."""
        #print("Pause!")
        pass

    def switchRecord(self):
        """Controls recording. Handles menu event."""
        # swap stat
        self.recording = not self.recording
        # emit signal
        self.record("", self.recording)
        # change menu
        if self.recording:
            label = "Stop Recording"
        else:
            label = "Record"
        self.popup.entryconfig(2, label=label)

    def show(self, x, y):
        """Handles right-click and opens menu.
        
        Arguments:
            x   X global coordinate.
            y   Y global coordinate.
        """
        # show menu
        try:
            self.popup.tk_popup(int(x), int(y), 0)
        # paint
        finally:
            self.popup.grab_release()





# called directly
if __name__ == '__main__':
    from globals import *
    raise NotCallableModuleError
    