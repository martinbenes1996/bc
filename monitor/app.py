
import fnmatch
import math
import numpy as np
import os
import re
import serial
import sys
import tkinter as tk
from tkinter import ttk
import time

from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg)
from matplotlib.figure import Figure
from matplotlib.backend_bases import key_press_handler
import matplotlib.pyplot as plt

import comm
import comm_serial
import comm_mcast
import record
import ui
import views
sys.path.insert(0, '../collector-py/')
import log
import conf



class App:
    """View of the client and window at once. Singleton.
    
    Attributes:
        app_                Main app to call mainloop() on.
        root                Master element.
        getReader           Callback for getting reader instance.
        getRecorder         Callback for getting recorder instance.
        window              Main window of app.
        serials             Serial port checkbuttons.
        serialfiles         Serial port names.
        tabControl          Tab control.
        tabs                Opened views of serial ports. Mapped {portname : TKinter Frame}.
        status              Statusbar.
        statusmsg           Message to show in statusbar.
    """
    app_ = None # app instance

    def __init__(self, master):
        """Constructor.
        
        Keyword arguments:
            master      Master of app. Tkinter element it should show in.
        """
        # instatiate window
        self.root = master
        w,h = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        self.root.geometry("%dx%d+0+0" % (w,h))

        # fill and display window
        self.create_window()
        # run timer for painting
        self.update_window()

        # create variables
        self.getReader = lambda _ : None
        self.getRecorder = lambda _ : None

    @classmethod
    def get(cls):
        """Instance getter."""
        # instantiate if not instanced yet
        if cls.app_ == None:
            cls.app_ = cls(tk.Tk())
        return cls.app_

    def create_window(self):
        """Creates window content."""
        # main window
        self.window = tk.Frame(self.root)
        # menu
        self.create_menu()
        # sources
        self.create_multicast()
        self.create_serial()
        # main view
        self.create_main()
        # recorder view
        self.create_recorderview()
    
    def create_menu(self):
        """Creates top menu."""
        menu = ui.Menu(self.root)
        menu.addDropdown( {'name':'File','content':{'Record':self.startRecordingSession,'Exit':self.root.quit}} )
        menu.addDropdown( {'name':'Help','content':{'About':self.showAbout}} )
    
    def create_multicast(self):
        tk.Label(self.root, text=u"Multicast channel", font=30).grid(column=0, sticky=tk.W+tk.N, padx=30)
        btnname = "M:"+str(conf.Config.channel())
        self.checkbutton_mcast = ui.CheckButton(self.root, btnname)
        self.checkbutton_mcast.checked, self.checkbutton_mcast.unchecked = self.create_tab, self.close_tab
        self.checkbutton_mcast.button.grid(column=0, sticky=tk.W+tk.N, padx=30)
        self.checkbutton_mcast.run()


    def create_serial(self):
        """Creates serial port view."""
        self.serialView = views.SerialMenu(self.root)
        self.serialView.begin(self.create_tab, self.close_tab)
            
    def create_main(self):
        """Creates main view."""
        # create tab control
        self.tabControl = ttk.Notebook(self.root)
        self.tabControl.grid(row=0, column=1, sticky=tk.W+tk.N, rowspan=20)
        self.tabs = {}

    def create_tab(self, name):
        """Creates one tab from checked serial port.
        
        Keyword arguments:
            name        Serial port name.
        """
        # check if not opened already
        if name in self.tabs:
            raise Exception("Opening existing tab!")

        # create frame
        tab = tk.Frame(self.tabControl)
        # get handlers
        reader,recorder = self.getReader(name).getSegment, self.getReader(name).record


        # create signal view
        self.create_signalview(tab, reader, recorder)
        # add to tab control
        self.tabControl.add(tab, text=name)
        self.tabs[name] = tab

    def close_tab(self, name):
        """Closes one tab from unchecked serial port.
        
        Keyword arguments:
            name        Serial port name.
        """
        # check if opened
        if name not in self.tabs:
            raise Exception("Closing not existing tab!")

        # remove from tab control
        self.tabControl.forget(self.tabs[name])
        # deallocate
        self.tabs[name].destroy()
        del self.tabs[name]
    
    def create_signalview(self, master, reader, recorder):
        """Creates view of signal on serial port.
        
        Keyword arguments:
            master      Element to show in.
            reader      Callback for getting data.
            recorder    Callback to control recording.
        """
        # create view
        sv = SignalView(self.root, master, reader, recorder)
        # place view
        sv.canvas.get_tk_widget().grid(row=0, column=1, rowspan=20, sticky=tk.N)

    def create_recorderview(self):
        self.recorderView = record.View(self.root, self.switchRecording)

    def startRecordingSession(self):
        # disable view
        tabid = self.tabControl.select()
        if not tabid:
            return
        tabName = self.tabControl.tab(tabid, "text")
        self.recorderView.begin(tabName, self.getRecorder(tabName))
    
    def switchRecording(self, recording):
        if recording:
            self.serialView.disable()
        else:
            self.serialView.update()


    def showAbout(self):
        """Shows help."""
        pass
    
    def update_window(self):
        """Updates window."""
        self.root.after(500, self.update_window)
    
    def mainloop(self):
        """Initializes TKinter event loop."""
        self.root.mainloop()






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
    

class CwtView:
    """View of CWT of signal on serial port.
    
    Attributes:
        master      Item to show in.
        viewer      View object from collector.
        canvas      Connection of TKinter and MatPlotLib.
        getData     Callback for updating data.
        record      Callback to control recording.
        afterId     TKinter ID of planned update.
    """
    def __init__(self, root, master, cwt, recorder):
        """Constructs object.
        
        Arguments:
            root        Root of view.
            master      Item to show in.
            cwt         Callback for updating data.
            recorder    Callback to control recording.
        """
        # generate variables
        self.master = master
        self.getData = cwt
        self.record = recorder
        self.menu = RightMenu(self.master, self.manualUpdate, self.recordMenuHandler)
        self.afterId = None

        # generate log view from collector
        self.viewer = log.Viewer(inline=True)
        # connection TKinter to MatPlotLib
        self.canvas = FigureCanvasTkAgg(self.viewer.cwt_fig, master=self.master)
        self.canvas.draw()
        # register event handlers
        self.canvas.get_tk_widget().bind('<ButtonRelease-1>', self.manualUpdate)
        self.canvas.get_tk_widget().bind('<ButtonRelease-3>', self.showMenu)
        # set border
        self.canvas.get_tk_widget().config(highlightcolor='black', highlightbackground='black', highlightthickness=3, bd=0)
    
        # run updater thread        
        self.update()
    
    def __del__(self):
        """Destructs object."""
        # finish updater thread
        if self.afterId:
            self.master.after_cancel(self.afterId)

    def show(self, data):
        """Actualizes view with new data.
        
        Arguments:
            data    New data.
        """
        # update viewer
        self.viewer.cwt(data)
        # paint
        self.canvas.draw()
        self.canvas.flush_events()
        #print("CwtView: update")

    def update(self):
        """Updates view. Runs in separate thread."""
        # actualize
        self.show( self.getData() )
        # next update in 200 ms
        self.afterId = self.master.after(200, self.update)

    def manualUpdate(self, event):
        """Manual update. Handles menu event.
        
        Arguments:
            event       Event descriptor.
        """
        if self.afterId:
            self.master.after_cancel(self.afterId)
        self.update()
    
    def showMenu(self, event):
        """Shows menu. Handles menu event.
        
        Arguments:
            event       Event descriptor.
        """
        # show menu
        self.menu.show(event.x_root, event.y_root)
    
    def recordMenuHandler(self, filename, status):
        """Catches event from menu to indicate recording to user.
        
        Arguments:
            filename    Filename of recording.
            status      True if turning on. False if turning off.
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



    