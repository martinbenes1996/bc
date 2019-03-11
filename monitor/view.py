
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

    class MemFunction:
        def __init__(self, f, arg1):
            self.f = f
            self.arg1 = arg1
        def __call__(self):
            self.f(self.arg1)

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
        self.handlers = {}

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
        # status bar
        #self.create_statusbar()
    
    def create_menu(self):
        """Creates top menu."""
        # Menu
        menubar = tk.Menu(self.root)
        # Menu Items
        # File
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Record", command=self.startRecordingSession)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=filemenu)
        # Help
        helpmenu = tk.Menu(menubar, tearoff=0)
        helpmenu.add_command(label="About", command=self.showAbout)
        menubar.add_cascade(label="Help", menu=helpmenu)
        # add menu to window
        self.root.config(menu=menubar)
    
    def create_multicast(self):
        tk.Label(self.root, text=u"Multicast channel", font=30).grid(column=0, sticky=tk.W+tk.N, padx=30)
        btnname = "M:"+str(conf.Config.channel())
        self.checkbutton_mcast = ui.CheckButton(self.root, btnname)
        self.checkbutton_mcast.checked, self.checkbutton_mcast.unchecked = self.create_tab, self.close_tab
        self.checkbutton_mcast.button.grid(column=0, sticky=tk.W+tk.N, padx=30)
        self.checkbutton_mcast.run()


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
            checkbutton = ui.CheckButton(self.root, "S:/dev/" + f)
            checkbutton.checked, checkbutton.unchecked = self.create_tab, self.close_tab
            checkbutton.alive = comm_serial.Reader.getReader
            checkbutton.button.grid(column=0, sticky=tk.W+tk.S, padx=30)
            checkbutton.run()
            self.serials.append(checkbutton)
            
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

    #def create_cwtview(self, master, cwt, recorder):
    #   """Creates view of CWT feature matrix.
    #   Keyword arguments:
    #       master      Element to show in.
    #       cwt         Callback for getting data.
    #       recorder    Callback to control recording. 
    #   """
    #   # create view
    #   cv = CwtView(self.root, master, cwt, recorder)
    #   # place view
    #   cv.canvas.get_tk_widget().grid(row=0, column=2, rowspan=20, sticky=tk.N)
    
    #def create_statusbar(self):
    #    """Creates statusbar."""
    #    # create statusbar
    #    self.status = tk.Label(self.root, text="Loading...", width=100, bd=1, relief=tk.SUNKEN, anchor=tk.W)
    #    # place
    #    self.root.grid_rowconfigure(100, weight=1)
    #    self.status.grid(row=100, column=0, columnspan=2, sticky=tk.S+tk.W+tk.E)
    #    # initiate
    #    self.statusmsg = ''
    #    #self.updateStatus()

    #def setStatus(self, status):
    #    """Sets status. Actualized by separate thread.
    #
    #    Keyword arguments:
    #        status      Message to show.
    #    """
    #    # set status
    #    self.statusmsg = status
    
    #def updateStatus(self):
    #    """Actualizes status. Runs in separate thread."""
    #    # no status to show
    #    while True:
    #        # nothing to show
    #        if self.statusmsg == '':
    #            time.sleep(0.1)
    #        # show status
    #        else:
    #            self.status.config(text=self.statusmsg)
    #            self.statusmsg = ''
    #            time.sleep(0.2)
    #            self.status.config(text='')

    def startRecordingSession(self):
        # disable view
        tabid = self.tabControl.select()
        tabName = self.tabControl.tab(tabid, "text")
        if not tabName:
            return
        activeTab = self.tabs[tabName]
        signalRecorder, cwtRecorder = self.handlers[tabName]
        self.switchRecording(True)
        self.tabControl.tab(tabid, state=tk.NORMAL)

        self.recorder = record.Recorder(signalRecorder, cwtRecorder)
        self.measurements = []

        self.recordFrame = tk.Frame(self.root, highlightcolor='black', highlightbackground='black', highlightthickness=3, bd=0)
        self.recordFrame.grid(row=0, column=3, rowspan=100, sticky=tk.N+tk.S+tk.E)
        self.headerFrame = tk.Label(self.recordFrame, text=u"Recording: "+tabName, font=30).grid(row=0, column=0, sticky=tk.N+tk.W)
        self.closeRecord = tk.Button(self.recordFrame, text="Close", command=self.endRecordingSession).grid(row=0, column=1, sticky=tk.N+tk.E)

        self.sessionName = tk.Text(self.recordFrame, height=1, width=40)
        self.sessionName.insert(tk.INSERT, self.recorder.generateSessionName())
        self.sessionName.grid(columnspan=2, sticky=tk.N+tk.W)

        self.recordBtn = tk.Button(self.recordFrame, text="Record", command=self.startRecording)
        self.recordBtn.grid(columnspan=2, sticky=tk.N+tk.E+tk.W)

        self.loadBtn = tk.Button(self.recordFrame, text="Load from file", command=self.loadSession)
        self.loadBtn.grid(columnspan=2, sticky=tk.N+tk.E+tk.W)
        self.addBtn = tk.Button(self.recordFrame, text="Add measurement", command=self.addMeasurement)
        self.addBtn.grid(columnspan=2, sticky=tk.N+tk.E+tk.W)
        self.saveBtn = tk.Button(self.recordFrame, text="Save to file", command=self.saveSession)
        self.saveBtn.grid(columnspan=2, sticky=tk.N+tk.E+tk.W)
    
    def endRecordingSession(self):
        del self.recorder
        del self.measurements
        self.recordFrame.destroy()
        del self.recordFrame
        self.switchRecording(False)
    
    def startRecording(self):
        self.recordBtn.config(text='Stop Recording', command=self.stopRecording)
        self.recordFrame.config(highlightcolor='red', highlightbackground='red')
        self.recorder.start(self.getSession(), self.recordSlave_markMeasurement, self.recordSlave_markDelay)
    

    def recordSlave_unmarkAll(self):
        for m in self.measurements:
            m['delayFrame'].config(highlightcolor='black', highlightbackground='black')
            m['frame'].config(highlightcolor='black', highlightbackground='black')
    def recordSlave_markMeasurement(self, i):
        self.recordSlave_unmarkAll()
        if i == len(self.measurements):
            return
        self.measurements[i]['frame'].config(highlightcolor='red', highlightbackground='red')
    def recordSlave_markDelay(self, i):
        self.recordSlave_unmarkAll()
        if i == len(self.measurements):
            return
        self.measurements[i]['delayFrame'].config(highlightcolor='red', highlightbackground='red')
    
    def stopRecording(self):
        self.recordBtn.config(text='Record', command=self.startRecording)
        self.recordFrame.config(highlightcolor='black', highlightbackground='black')

    def addMeasurement(self, value = {'name' : '', 'time' : 5, 'delay' : 10, 'signal' : True, 'cwt' : False}):
        self.addBtn.grid_forget()
        self.saveBtn.grid_forget()

        measurement = {}
        
        measurement['delayFrame'] = tk.Frame(self.recordFrame, highlightcolor='black', highlightbackground='black', highlightthickness=1, bd=0)
        tk.Label(measurement['delayFrame'], text=u"Delay [s]:").grid(sticky=tk.W)
        measurement['delay'] = tk.Text(measurement['delayFrame'], height=1, width=20)
        measurement['delay'].insert(tk.INSERT, str(value['delay']))
        measurement['delay'].grid(row=2, column=1, columnspan=2, sticky=tk.W+tk.N)
        measurement['delayFrame'].grid(columnspan=2, sticky=tk.N)

        measurement['frame'] = tk.Frame(self.recordFrame, highlightcolor='black', highlightbackground='black', highlightthickness=1, bd=0)
        measurement['frame'].grid(columnspan=2, sticky=tk.N)

        tk.Label(measurement['frame'], text=u"Measurement", font=25).grid(row=0, column=0, sticky=tk.N+tk.W)

        measurement['close'] = tk.Button(measurement['frame'], text="X", command=self.MemFunction(self.deleteMeasurement,len(self.measurements)))
        measurement['close'].grid(row=0, column=2, sticky=tk.E+tk.N)

        tk.Label(measurement['frame'], text=u"Name:").grid(sticky=tk.W)
        measurement['name'] = tk.Text(measurement['frame'], height=1, width=20)
        measurement['name'].insert(tk.INSERT, value['name'])
        measurement['name'].grid(row=1, column=1, sticky=tk.W+tk.N)        

        tk.Label(measurement['frame'], text=u"Length [s]:").grid(sticky=tk.W)
        measurement['time'] = tk.Text(measurement['frame'], height=1, width=20)
        measurement['time'].insert(tk.INSERT, str(value['time']))
        measurement['time'].grid(row=2, column=1, columnspan=2, sticky=tk.W+tk.N)

        measurement['signalVal'] = tk.IntVar()
        measurement['cwtVal'] = tk.IntVar()
        measurement['signalVal'].set( int(value['signal']) )
        measurement['cwtVal'].set( int(value['cwt']) )

        measurement['signal'] = ttk.Checkbutton(measurement['frame'], text="Signal", variable=measurement['signalVal'])
        measurement['signal'].grid(row=3, column=1, columnspan=2, sticky=tk.W+tk.N)
        measurement['cwt'] = ttk.Checkbutton(measurement['frame'], text="CWT", variable=measurement['cwtVal'])
        measurement['cwt'].grid(row=4, column=1, columnspan=2, sticky=tk.W+tk.N)
        
        self.measurements.append(measurement)


        self.addBtn.grid(columnspan=2, sticky=tk.N+tk.E+tk.W)
        self.saveBtn.grid(columnspan=2, sticky=tk.N+tk.E+tk.W)

    def deleteMeasurement(self, index):
        self.measurements[index]['delayFrame'].destroy()
        self.measurements[index]['frame'].destroy()
        del self.measurements[index]
        
        for i,m in enumerate(self.measurements):
            m['close'].config(command=self.MemFunction(self.deleteMeasurement, i))

    def loadSession(self):
        filename = self.sessionName.get("1.0","end-1c")

        session = self.recorder.loadSession(filename)

        self.sessionName.delete('1.0', tk.END)
        self.sessionName.insert(tk.INSERT, session['name'])
        for _ in self.measurements:
            self.deleteMeasurement(0)
        for it in session['measurements']:
            self.addMeasurement(it)

        # show file content in view
        # ...
    
    def getSession(self):
        session = {'measurements' : []}

        session['name'] = self.sessionName.get("1.0","end-1c")
        print("Save session", session['name'])
        
        for m in self.measurements:
            d = {}
            d['delay'] = int(m['delay'].get("1.0", "end-1c"))
            d['name'] = m['name'].get("1.0","end-1c")
            d['time'] = int(m['time'].get("1.0", "end-1c"))
            d['signal'] = bool(m['signal'].state())
            d['cwt'] = bool(m['cwt'].state())
            session['measurements'].append(d)
        return session

    def saveSession(self):
        self.recorder.saveSession(self.getSession())
    
    def switchRecording(self, recording):
        if recording:
            for chb in self.serials:
                chb.disable()
        else:
            for chb in self.serials:
                chb.manualUpdate()


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



    