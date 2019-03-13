
import os
import re
import sys

import tkinter as tk

from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg)
from matplotlib.figure import Figure
from matplotlib.backend_bases import key_press_handler
import matplotlib.pyplot as plt

import comm_serial
import conf
import ui
sys.path.insert(0, '../collector-py/')
import log

class SerialView:
    def __init__(self, root):
        self.root = root
        self.serials = []

    def begin(self, create, close):
        # look up serials
        allfiles = re.findall(r'ttyS[0-9]+', ",".join(os.listdir("/dev/")))
        # sort serial files by numeric appendix numerically
        serialfiles = sorted(allfiles, key=self.sortByNumericAppendix)
        # headline
        tk.Label(self.root, text=u"Ports", font=30).grid(column=0, sticky=tk.W+tk.S, padx=30)

        # generate checkbutons
        for f in serialfiles:
            checkbutton = ui.CheckButton(self.root, "S:/dev/" + f)
            checkbutton.checked, checkbutton.unchecked = create, close
            checkbutton.alive = comm_serial.Reader.getReader
            checkbutton.button.grid(column=0, sticky=tk.W+tk.S, padx=30)
            checkbutton.run()
            self.serials.append(checkbutton)
    
    def disable(self):
        for chb in self.serials:
            chb.disable()
    def update(self):
        for chb in self.serials:
            chb.manualUpdate()
        

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
    
    def begin(self, create, close):
        tk.Label(self.root, text=u"Multicast channel", font=30).grid(column=0, sticky=tk.W+tk.N, padx=30)
        btnname = "M:"+str(conf.Config.channel())
        self.checkbutton_mcast = ui.CheckButton(self.root, btnname)
        self.checkbutton_mcast.checked, self.checkbutton_mcast.unchecked = create, close
        self.checkbutton_mcast.button.grid(column=0, sticky=tk.W+tk.N, padx=30)
        self.checkbutton_mcast.run()



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
        self.afterId = self.master.after(300, self.update)

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

