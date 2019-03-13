
import tkinter as tk

class CheckButton:
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
    def __init__(self, master, name):
        """Constructs object.
        
        Arguments:
            master      Item to show in.
            name        ID. Text to show.
            callCheck   Callback to call when checked.
            callUncheck Callback to call when unchecked
        """
        # create variables
        self.master = master
        self.name = name

        # initialize
        self.checked = lambda name : None
        self.unchecked = lambda name : None
        self.alive = lambda name : None
        self.threadid = None
        
        # create button
        self.var = tk.IntVar()
        self.button = tk.Checkbutton(self.master, text=self.name, command=self.changed, variable=self.var)
        # run update in separate thread
        

    def __del__(self):
        """Destructs object."""
        # finish separate thread
        self.stopUpdate()
    def stopUpdate(self):
        if self.threadid:
            self.master.after_cancel(self.threadid)
        self.threadid = None

    def changed(self):
        """Handles check/uncheck event."""
        # checked
        if self.var.get():
            self.checked(self.name)
        # unchecked
        else:
            self.checked(self.name)
    
    def update(self):
        """Updates checkbutton availability status."""
        # try to connect
        try:
            self.alive(self.name)
        # failed
        except Exception as e:
            self.button.config(state=tk.DISABLED)
        # connected
        else:
            self.button.config(state=tk.NORMAL)
        # do again in 30s
        self.threadid = self.master.after(30000, self.update)
    
    def run(self):
        self.stopUpdate()
        self.update()
    def disable(self):
        self.stopUpdate()
        self.button.config(state=tk.DISABLED)


class Menu():
    def __init__(self, root):
        self.menubar = tk.Menu(root)
        root.config(menu=self.menubar)
    def addDropdown(self, dropdown):
        menu = tk.Menu(self.menubar, tearoff=0)
        for l,c in dropdown['content'].items():
            menu.add_command(label=l, command=c)
        self.menubar.add_cascade(label=dropdown['name'], menu=menu)