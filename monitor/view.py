
import fnmatch
import math
import numpy as np
import os
import re
import tkinter as tk
from tkinter import ttk
import time

from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg)
from matplotlib.figure import Figure
from matplotlib.backend_bases import key_press_handler
import matplotlib.pyplot as plt


class App:
    """View of the client and window at once. Singleton.
    
    Attributes:
        app_    Main app to call mainloop() on.
    """
    app_ = None # app instance
    def __init__(self, master, *args, **kwargs):
        """Constructor.
        
        Keyword arguments:
            master      Master of app. None defaultly.
        """
        # instatiate window
        self.root = master
        w,h = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        #self.root.overrideredirect(1)
        self.root.geometry("%dx%d+0+0" % (w,h))

        # fill and display window
        self.create_window()
        # run timer for painting
        self.update_window()
        self.updaters = []

        # create variables
        self.readers = {}
        self.cwt = {}

    @classmethod
    def get(cls):
        """Instance getter."""
        # instantiate if not instanced yet
        if cls.app_ == None:
            cls.app_ = cls(tk.Tk())
        return cls.app_

    def create_window(self):
        """Creates window content."""
        self.window = tk.Frame(self.root)
        self.create_menu()
        self.create_serial()
        self.create_main()
    
    def create_menu(self):
        menubar = tk.Menu(self.root)
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
        self.serials = []
        allfiles = re.findall(r'ttyS[0-9]+', ",".join(os.listdir("/dev/")))

        def sortByNumericAppendix(name):
            try:
                n = re.search(r'(?<=ttyS)[0-9]+', name)
            except:
                print("Error: sortByNumericAppendix(", name, ")")
                return 0
            #print("compare", name, n.group(0))
            return int( n.group(0) )

        self.serialfiles = sorted(allfiles, key=sortByNumericAppendix)

        for f in self.serialfiles:
            checkbutton = MyCheckButton(self.root, f, self.checkSerial, self.uncheckSerial)
            checkbutton.button.grid(column=0, sticky=tk.W+tk.S, padx=30)
            self.serials.append(checkbutton)

    

    def create_main(self):
        self.tabControl = ttk.Notebook(self.root)
        self.tabControl.grid(row=0, column=1, sticky=tk.W+tk.N,rowspan=30)
        self.tabs = {}

    def checkSerial(self, name):
        self.create_tab("/dev/" + name)

    def uncheckSerial(self, name):
        self.close_tab("/dev/" + name)

    def create_tab(self, name):
        if name in self.tabs:
            raise Exception("Opening existing tab!")
        tab = tk.Frame(self.tabControl)
        reader = lambda:[0 for _ in range(0,60)]
        cwt = lambda:[[0 for _ in range(0,60)] for _ in range(0,500)]

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

        self.create_signalview(tab, reader)
        self.create_cwtview(tab,cwt)
        self.tabControl.add(tab, text=name)
        self.tabs[name] = tab

    def close_tab(self, name):
        if name not in self.tabs:
            raise Exception("Closing not existing tab!")
        self.tabControl.forget(self.tabs[name])
        self.tabs[name].destroy()
        del self.tabs[name]
    
    def create_signalview(self, master, reader):
        sv = SignalView(self.root, master, reader)
        sv.canvas.get_tk_widget().grid(row=0, column=1, rowspan=30)
    def create_cwtview(self, master, cwt):
        cv = CwtView(self.root, master, cwt)
        cv.canvas.get_tk_widget().grid(row=0, column=2, rowspan=30)

    def showAbout(self):
        pass
    
    def update_window(self):

        self.root.after(500, self.update_window)
    
    def mainloop(self):
        self.root.mainloop()



class MyCheckButton:
    def __init__(self, master, text, callCheck, callUncheck):
        self.master = master
        self.text = text
        self.callCheck, self.callUncheck = callCheck, callUncheck
        self.var = tk.IntVar()
        self.button = tk.Checkbutton(self.master, text=self.text, command=self.changed, variable=self.var)

    def changed(self):
        if self.var.get():
            self.callCheck(self.text)
        else:
            self.callUncheck(self.text)


class SignalView:
    def __init__(self, root, master, reader):
        self.master = master
        self.fig = Figure(figsize=(5,4), dpi=100)
        self.subplt = self.fig.add_subplot(111)
        self.subplt.set_ylim(0, 1027)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.master)
        self.canvas.draw()
        self.canvas.mpl_connect("key_press_event", self.onMouseClick)
        self.getData = reader

        self.afterId = None
        self.update()
    
    def __del__(self):
        if self.afterId:
            self.master.after_cancel(self.afterId)
        
    
    def show(self, data):
        print("SignalView: update")
        self.subplt.cla()
        self.subplt.set_ylim(0, 1027)
        self.subplt.plot(data, color='magenta')
        self.canvas.draw()
        self.canvas.flush_events()
        
    def update(self):
        self.show( self.getData() )
        self.afterId = self.master.after(500, self.update)
    
    def onMouseClick(self):
        pass
    
    

class CwtView:
    def __init__(self, root, master, cwt):
        self.master = master
        self.fig = Figure(figsize=(5,4), dpi=100)
        self.subplt = self.fig.add_subplot(111)
        self.subplt.set_ylim(0,4)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.master)
        self.canvas.draw()
        self.canvas.mpl_connect("key_press_event", self.onMouseClick)
        self.getData = cwt

        self.afterId = None
        #self.update()
    
    def show(self, data):
        print("CwtView: update")
        self.subplt.cla()
        self.subplt.set_ylim(0, 4)
        self.subplt.plot(data, color='magenta')
        self.canvas.draw()
        self.canvas.flush_events()
        
    def update(self):
        self.show( self.getData() )
        self.afterId = self.master.after(500, self.update)
    
    def onMouseClick(self):
        pass


    