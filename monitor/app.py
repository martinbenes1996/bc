
import tkinter as tk
from tkinter import ttk

import record
import ui
import views



class App:
    """View of the client and window at once. Singleton.
    
    Attributes:
        app_                Main app to call mainloop() on.
        root                Master element.
        getReader           Callback for getting reader instance.
        getRecorder         Callback for getting recorder instance.
        window              Main window of app.
        tabControl          Tab control.
        tabs                Opened views of serial ports. Mapped {portname : TKinter Frame}.
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
        self.create_multicastview()
        self.create_serialview()
        # main view
        self.create_main()
        # recorder view
        self.create_recorderview()
    
    def create_menu(self):
        """Creates top menu."""
        menu = ui.Menu(self.root)
        menu.addDropdown( {'name':'File','content':{'Record':self.startRecordingSession,'Exit':self.root.quit}} )
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
        reader,recorder = self.getReader(name), self.getRecorder(name)

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
        sv = views.SignalView(self.root, master, reader, recorder)
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
        self.root.after(1000, self.update_window)
    
    def mainloop(self):
        """Initializes TKinter event loop."""
        self.root.mainloop()



    