

"""
File:           ui.py
Author:         Martin Benes
Institution:    Faculty of Information Technology
                Brno University of Technology

This module contains classes implementing basic graphical entities for view.
Developed as a part of bachelor thesis "Counting of people using PIR sensor".
"""

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
        print(self.var.get())
        # checked
        if self.var.get():
            self.checked(self.name)
        # unchecked
        else:
            self.unchecked(self.name)
    
    def update(self):
        """Updates checkbutton availability status."""
        # try to connect
        try:
            self.alive(self.name[2:])
        # failed
        except Exception as e:
            self.button.config(state=tk.DISABLED)
        # connected
        else:
            self.button.config(state=tk.NORMAL)
        # do again in 30s
        self.threadid = self.master.after(30000, self.update)
    
    def run(self):
        """Restarts updating."""
        self.stopUpdate()
        self.update()
    def disable(self):
        """Disables the button. Stops updating."""
        self.stopUpdate()
        self.button.config(state=tk.DISABLED)


class Menu():
    """Menu of the app.
    
    Attributes:
        menubar     TKinter menu bar.
    """
    def __init__(self, root):
        """Constructs and initializes the Menu.
        
        Arguments:
            root        Parent view object.
        """
        # create
        self.menubar = tk.Menu(root)
        # set as menu
        root.config(menu=self.menubar)

    def addDropdown(self, dropdown):
        """Create dropdown.
        
        Arguments:
            dropdown        Description of dropdown structure {label : function}.
        """
        # create dropdown
        menu = tk.Menu(self.menubar, tearoff=0)
        for l,c in dropdown['content'].items():
            menu.add_command(label=l, command=c)
        # add dropdown
        self.menubar.add_cascade(label=dropdown['name'], menu=menu)










# called directly
if __name__ == '__main__':
    from globals import *
    raise NotCallableModuleError
    