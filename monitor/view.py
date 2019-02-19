
import fnmatch
import math
import os
import re
import tkinter as tk
import time

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
                check = tk.Checkbutton(self.root, text=f)
                check.grid(column=0, sticky=tk.W+tk.S)
                self.serials.append(check)
                
    def create_tab(self):
        pass

    def showAbout(self):
        pass



    
    def update_window(self):
        # hide and delete all drawn objects
        #for o in self.objects:
        #    self.itemconfigure(o, state='hidden')
        #    self.delete(o)
        #self.objects = []
        # draw the new objects
        #print("App.update: objects", self.getData())
        #for o in self.getData():
        #    self.objects.append( self.add_object(*o) )
        self.root.after(500, self.update_window)
    
    def add_object(self, azimuth, distance):
        #print("App.create_object: azimuth", azimuth, "distance", distance)
        #r = 10
        #x0,y0 = self.polar2global(azimuth, distance)
        #x1,y1 = self.polar2global(azimuth, distance)
        #print("App.create_object: [",x0,y0,"] [",x1, y1,"]")
        #return self.create_oval(x0-r, y0+r, x1+r, y1-r, fill="#ffffff")
        pass
    
    def mainloop(self):
        self.root.mainloop()
