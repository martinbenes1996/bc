

"""
File:           app.py
Author:         Martin Benes
Institution:    Faculty of Information Technology
                Brno University of Technology

This module contains main view class - App.
Developed as a part of bachelor thesis "Counting of people using PIR sensor".
"""

import logging
import threading # delete
import sys

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog

import globals
import record
import ui
import views


class App:
    """View of the client and window at once. Singleton.
    
    Static attributes:
        app_                Main app to call mainloop() on.
    Attributes:
        getReader           Callback for getting reader instance.
        getRecorder         Callback for getting recorder instance.
        getExtractor        Callback for getting extractor instance.
        getReplayer         Callback for getting replayer instance.
        multicastView       View for multicast.
        recorderView        View for recorder.
        root                Master element.
        serialView          View for serial.
        tabControl          Tab control.
        tabs                Opened views of serial ports. Mapped {portname : TKinter Frame}.
        window              Main window of app.
    """
    app_ = None # app instance
    log = logging.getLogger(__name__)

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
        self.getExtractor = lambda _ : None
        self.getReplayer = lambda _ : None

    @classmethod
    def get(cls):
        """Instance getter."""
        # instantiate if not instanced yet
        if cls.app_ == None:
            root = tk.Tk()
            cls.app_ = cls(root)
            root.protocol("WM_DELETE_WINDOW",cls.close_window)
        return cls.app_

    def create_window(self):
        """Creates window content."""
        # main window
        self.window = tk.Frame(self.root)
        # menu
        self.create_menu()
        # sources
        self.create_multicastview()
        self.create_serialview()
        # main view
        self.create_main()
        # recorder view
        self.create_recorderview()
    
    def create_menu(self):
        """Creates top menu."""
        menu = ui.Menu(self.root)
        menu.addDropdown( {'name':'File','content':{'Replay...':self.startReplaySession, 'Record':self.startRecordingSession,'Exit':self.close_window}} )
        menu.addDropdown( {'name':'Help','content':{'About':self.showAbout}} )
    
    def create_multicastview(self):
        """Creates serial port view."""
        self.multicastView = views.MulticastView(self.root)
        self.multicastView.begin(self.create_tab, self.close_tab)

    def create_serialview(self):
        """Creates serial port view."""
        self.serialView = views.SerialView(self.root)
        self.serialView.begin(self.create_tab, self.close_tab)
            
    def create_main(self):
        """Creates main view."""
        # create tab control
        self.tabControl = ui.Notebook(self.root, onclose=self.close_tab)
        self.tabControl.grid(row=0, column=1, sticky=tk.W+tk.N, rowspan=20)
        self.tabs = {}

    def create_tab(self, name, replayview=False):
        """Creates one tab.
        
        Keyword arguments:
            name        Source name.
            replayview  Indicator of showing replay view.
        """
        # check if not opened already
        if name in self.tabs:
            raise Exception("Opening existing tab!")

        # create frame
        tab = tk.Frame(self.tabControl)
        # get handlers
        reader,recorder = self.getReader(name), self.getRecorder(name)
        extractor = self.getExtractor(name)
        replayer = self.getReplayer(name)
        
        # create signal view
        self.create_signalview(tab, reader, recorder)
        # create area view
        self.create_areaview(tab, extractor)
        #create replay view
        if replayview:
            self.create_replayview(tab, replayer)
        # add to tab control
        self.tabControl.add(tab, text=name)
        self.tabs[name] = tab

    def close_tab(self, name):
        """Closes one tab from unchecked tab.
        
        Keyword arguments:
            name        Tab name.
        """
        self.serialView.uncheck(name)
        self.multicastView.uncheck(name)
        try:
            # remove from tab control
            self.tabControl.forget(self.tabs[name])
            # deallocate
            self.tabs[name].destroy()
            del self.tabs[name]

        # does not exist
        except KeyError:
            self.log.error("closing not existing tab")

    def create_signalview(self, master, reader, recorder):
        """Creates view of signal on serial port.
        
        Keyword arguments:
            master      Element to show in.
            reader      Callback for getting data.
            recorder    Callback to control recording.
        """
        # create view
        sv = views.SignalView(self.root, master, reader, recorder)
        # place view
        sv.canvas.get_tk_widget().grid(row=0, column=1, rowspan=20, sticky=tk.N)

    def create_areaview(self, master, reader):
        """Creates view of sensed area represented by matrix.
        
        Keyword arguments:
            master      Element to show in.
            reader      Callback for getting data.
        """
        # create view
        sv = views.AreaView(master, reader)
        # place view
        sv.canvas.get_tk_widget().grid(row=0, column=2, rowspan=20, sticky=tk.N)

    def create_replayview(self, master, replayer):
        """Creates controller for replaying.
        
        Keyword arguments:
            master      Element to show in.
            replayer    Callback for restarting the replaying.
        """
        # create view
        rv = views.ReplayView(master, replayer)
        rv.frame.grid(row=0,column=3, sticky=tk.N)
    def startReplaySession(self):
        """Starts the replaying session, opens the file dialog."""
        replayfile = tk.filedialog.askopenfilename(initialdir='../data',title='Load recording',filetypes=(('Recordings (.csv)','*.csv'),) )
        self.create_tab(replayfile, replayview=True)

    def create_recorderview(self):
        """Creates view for recording"""
        self.recorderView = record.View(self.root, self.switchRecording)
    def startRecordingSession(self):
        """Starts the recording session (after clicking the record button)."""
        # disable view
        tabid = self.tabControl.select()
        if not tabid:
            return
        tabName = self.tabControl.tab(tabid, "text")
        self.recorderView.begin(tabName, self.getRecorder(tabName))
    def switchRecording(self, recording):
        """Disables the serial view during recording session.
        
        Keyword arguments:
            recording   If serial view is visible or not.
        """
        if recording:
            self.serialView.disable()
        else:
            self.serialView.update()

    def showAbout(self):
        """Shows help."""
        pass
    
    def update_window(self):
        """Updates window."""
        self.root.after(1000, self.update_window)
        if globals.quit == True:
            self.close_window()
    @classmethod
    def close_window(cls):
        """Handler for window closing."""
        cls.log.info("window closed")
        cls.app_.root.destroy()
        globals.quit = True
        for t in threading.enumerate():
            try:
                t.join()
            except RuntimeError:
                pass
        sys.exit(0)

    
    def mainloop(self):
        """Initializes TKinter event loop."""
        self.root.mainloop()



    