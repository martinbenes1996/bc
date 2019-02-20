
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

import hw
sys.path.insert(0, '../collector-py/')
import log
import conf


class App:
    """View of the client and window at once. Singleton.
    
    Attributes:
        app_                Main app to call mainloop() on.
        root                Master element.
        readers             Callbacks for getting data from serial port. Mapped {portname : function}.
        cwt                 Callbacks for getting cwt coefficients. Mapped {portname : function}.
        signalrecorders     Callbacks for controlling recording of dataflow on serial port. Mapped {portname : function}.
        cwtrecorders        Callbacks for controlling recording of cwt coefficients. Mapped {portname : function}.
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
        self.readers = {}
        self.cwt = {}
        self.signalrecorders = {}
        self.cwtrecorders = {}

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
        # serial ports
        self.create_serial()
        # main view
        self.create_main()
        # status bar
        self.create_statusbar()
    
    def create_menu(self):
        """Creates top menu."""
        # Menu
        menubar = tk.Menu(self.root)
        # Menu Items
        # File
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=filemenu)
        # Help
        helpmenu = tk.Menu(menubar, tearoff=0)
        helpmenu.add_command(label="About", command=self.showAbout)
        menubar.add_cascade(label="Help", menu=helpmenu)
        # add menu to window
        self.root.config(menu=menubar)
    
    def create_serial(self):
        """Creates serial port view."""
        # look up serials
        self.serials = []
        allfiles = re.findall(r'ttyS[0-9]+', ",".join(os.listdir("/dev/")))

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
        # sort serial files by numeric appendix numerically
        self.serialfiles = sorted(allfiles, key=sortByNumericAppendix)
        # headlne
        tk.Label(self.root, text=u"Ports", font=30).grid(column=0, sticky=tk.W+tk.S, padx=30)
        # generate checkbutons
        for f in self.serialfiles:
            checkbutton = MyCheckButton(self.root, "/dev/" + f, self.create_tab, self.close_tab)
            checkbutton.button.grid(column=0, sticky=tk.W+tk.S, padx=30)
            self.serials.append(checkbutton)

    def create_main(self):
        """Creates main view."""
        # create tab control
        self.tabControl = ttk.Notebook(self.root)
        self.tabControl.grid(row=0, column=1, sticky=tk.W+tk.N,rowspan=30)
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
        reader = lambda:[0 for _ in range(0,60)]
        cwt = lambda:[[0 for _ in range(0,60)] for _ in range(0,500)]
        signalrecorder = lambda _:None
        cwtrecorder = lambda _:None
        if name in self.readers:
            print("Reader assigned.")
            reader = self.readers[name]
        else:
            print(name, "is not in", self.cwt)
        if name in self.cwt:
            print("Cwt assigned.")
            cwt = self.cwt[name]
        else:
            print(name, "is not in", self.cwt)
        if name in self.signalrecorders:
            print("SignalRecorder assigned.")
            signalrecorder = self.signalrecorders[name]
        else:
            print(name, "is not in", self.signalrecorders)
        if name in self.cwtrecorders:
            print("CwtRecorder assigned.")
            cwtrecorder = self.cwtrecorders[name]
        else:
            print(name, "is not in", self.cwtrecorders)

        # create signal view
        self.create_signalview(tab, reader, signalrecorder)
        # create CWT view
        self.create_cwtview(tab,cwt, cwtrecorder)
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
        sv.canvas.get_tk_widget().grid(row=0, column=1, rowspan=30, sticky=tk.N)

    def create_cwtview(self, master, cwt, recorder):
        """Creates view of CWT feature matrix.

        Keyword arguments:
            master      Element to show in.
            cwt         Callback for getting data.
            recorder    Callback to control recording. 
        """
        # create view
        cv = CwtView(self.root, master, cwt, recorder)
        # place view
        cv.canvas.get_tk_widget().grid(row=0, column=2, rowspan=30, sticky=tk.N)
    
    def create_statusbar(self):
        """Creates statusbar."""
        # create statusbar
        self.status = tk.Label(self.root, text="Loading...", width=100, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        # place
        self.root.grid_rowconfigure(100, weight=1)
        self.status.grid(row=100, column=0, columnspan=2, sticky=tk.S+tk.W+tk.E)
        # initiate
        self.statusmsg = ''
        #self.updateStatus()

    def setStatus(self, status):
        """Sets status. Actualized by separate thread.

        Keyword arguments:
            status      Message to show.
        """
        # set status
        self.statusmsg = status
    
    def updateStatus(self):
        """Actualizes status. Runs in separate thread."""
        # no status to show
        while True:
            # nothing to show
            if self.statusmsg == '':
                time.sleep(0.1)
            # show status
            else:
                self.status.config(text=self.statusmsg)
                self.statusmsg = ''
                time.sleep(0.2)
                self.status.config(text='')
        

    def showAbout(self):
        """Shows help."""
        pass
    
    def update_window(self):
        """Updates window."""
        self.root.after(500, self.update_window)
    
    def mainloop(self):
        """Initializes TKinter event loop."""
        self.root.mainloop()



class MyCheckButton:
    """Checkbutton of serial port.
    
    Attributes:
        master          Item to show in.
        text            Displayed text.
        callCheck       Callback to call when checked.
        callUncheck     Callback to call when unchecked.
        var             State of checkbutton.
        afterId         TKinter ID of planned call.
        button          Checkbutton.
    """
    def __init__(self, master, text, callCheck, callUncheck):
        """Constructs object.
        
        Arguments:
            master      Item to show in.
            text        Displayed text.
            callCheck   Callback to call when checked.
            callUncheck Callback to call when unchecked
        """
        # create variables
        self.master = master
        self.text = text
        self.callCheck, self.callUncheck = callCheck, callUncheck
        self.var = tk.IntVar()
        self.afterId = None
        # create button
        self.button = tk.Checkbutton(self.master, text=self.text, command=self.changed, variable=self.var)
        # run update in separate thread
        self.update()

    def __del__(self):
        """Destructs object."""
        # finish separate thread
        if not self.afterId:
            self.master.after_cancel(self.afterId)

    def changed(self):
        """Handles check/uncheck event."""
        # checked
        if self.var.get():
            self.callCheck(self.text)
        # unchecked
        else:
            self.callUncheck(self.text)
    
    def update(self):
        """Updates checkbutton availability status."""
        # try to connect
        try:
            device = hw.Reader.getReader(self.text)
        # failed
        except serial.serialutil.SerialException:
            self.button.config(state=tk.DISABLED)
        # connected
        else:
            self.button.config(state=tk.NORMAL)
        # do again in 30s
        self.afterId = self.master.after(30000, self.update)


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
        self.fig = Figure(figsize=(5,4), dpi=100)
        self.subplt = self.fig.add_subplot(111)
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



    