
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
        self.create_statusbar()
    
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

        tk.Label(self.root, text=u"Ports", font=30).grid(column=0, sticky=tk.W+tk.S, padx=30)

        for f in self.serialfiles:
            checkbutton = MyCheckButton(self.root, "/dev/"+f, self.checkSerial, self.uncheckSerial)
            checkbutton.button.grid(column=0, sticky=tk.W+tk.S, padx=30)
            self.serials.append(checkbutton)

    

    def create_main(self):
        self.tabControl = ttk.Notebook(self.root)
        self.tabControl.grid(row=0, column=1, sticky=tk.W+tk.N,rowspan=30)
        self.tabs = {}

    def checkSerial(self, name):
        self.create_tab(name)

    def uncheckSerial(self, name):
        self.close_tab(name)

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
    
    def create_statusbar(self):
        self.status = tk.Label(self.root, text="Loading...", width=100, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.root.grid_rowconfigure(100, weight=1)
        self.status.grid(row=100, column=0, columnspan=2, sticky=tk.S+tk.W+tk.E)
        self.statusmsg = ''
        #self.updateStatus()

    def setStatus(self, status):
        self.statusmsg = status
    
    def updateStatus(self):
        if self.statusmsg == '':
            self.root.after(100, self.updateStatus)
        self.status.config(text=self.statusmsg)
        self.statusmsg = ''
        self.root.after(200, self.emptyStatus)

    def emptyStatus(self):
        self.status.config(text='')
        self.updateStatus()
        

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
        self.afterId = None
        self.button = tk.Checkbutton(self.master, text=self.text, command=self.changed, variable=self.var)
        self.update()

    def __del__(self):
        if not self.afterId:
            self.master.after_cancel(self.afterId)

    def changed(self):
        if self.var.get():
            self.callCheck(self.text)
        else:
            self.callUncheck(self.text)
    
    def update(self):
        try:
            device = hw.Reader.getReader(self.text)
        except serial.serialutil.SerialException:
            #self.button.config(fg="red")
            self.button.config(state=tk.DISABLED)
        else:
            #self.button.config(fg="green")
            self.button.config(state=tk.NORMAL)
        self.afterId = self.master.after(30000, self.update)


class SignalView:
    def __init__(self, root, master, reader):
        self.master = master
        self.fig = Figure(figsize=(5,4), dpi=100)
        self.subplt = self.fig.add_subplot(111)
        self.subplt.set_ylim(0, 1027)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.master)
        self.canvas.draw()
        self.canvas.get_tk_widget().bind('<ButtonRelease-1>', self.manualUpdate)
        self.canvas.get_tk_widget().bind('<ButtonRelease-3>', self.showMenu)
        self.getData = reader

        self.menu = RightMenu(self.master, self.manualUpdate)

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
        self.afterId = self.master.after(200, self.update)
    def manualUpdate(self, event):
        if self.afterId:
            self.master.after_cancel(self.afterId)
        self.update()
    
    def showMenu(self, event):
        self.menu.show(event.x_root, event.y_root)
    
    

class CwtView:
    def __init__(self, root, master, cwt):
        self.master = master
        self.viewer = log.Viewer(inline=True)
        self.canvas = FigureCanvasTkAgg(self.viewer.cwt_fig, master=self.master)
        self.canvas.draw()
        self.canvas.get_tk_widget().bind('<ButtonRelease-1>', self.manualUpdate)
        self.canvas.get_tk_widget().bind('<ButtonRelease-3>', self.showMenu)
        self.getData = cwt

        self.menu = RightMenu(self.master, self.manualUpdate)

        self.afterId = None
        self.update()
    
    def __del__(self):
        if self.afterId:
            self.master.after_cancel(self.afterId)

    def show(self, data):
        print("CwtView: update")
        self.viewer.cwt(data)
        self.canvas.draw()
        self.canvas.flush_events()

    def update(self):
        self.show( self.getData() )
        self.afterId = self.master.after(200, self.update)
    def manualUpdate(self, event):
        if self.afterId:
            self.master.after_cancel(self.afterId)
        self.update()
    
    def showMenu(self, event):
        self.menu.show(event.x_root, event.y_root)


class RightMenu:
    def __init__(self, master, refresh):
        self.popup = tk.Menu(master, tearoff=0)
        self.popup.add_command(label="Refresh", command=refresh)
        self.popup.add_command(label="Pause", command=self.pause)
        self.popup.add_command(label="Record", command=self.record)

    def pause(self):
        print("Pause!")
    def record(self):
        print("Record!")

    def show(self, x, y):
        try:
            self.popup.tk_popup(int(x), int(y), 0)
        finally:
            self.popup.grab_release()



    