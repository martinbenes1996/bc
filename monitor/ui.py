

"""
File:           ui.py
Author:         Martin Benes
Institution:    Faculty of Information Technology
                Brno University of Technology

This module contains classes implementing basic graphical entities for view.
Developed as a part of bachelor thesis "Counting of people using PIR sensor".
"""

import logging

import tkinter as tk
from tkinter import ttk

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
    log = logging.getLogger(__name__)
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
        """Stops the update loop."""
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
            self.unchecked(self.name)
    
    def off(self):
        """Deselects the check button."""
        self.button.deselect()
    
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


# https://stackoverflow.com/questions/39458337/is-there-a-way-to-add-close-buttons-to-tabs-in-tkinter-ttk-notebook
class Notebook(ttk.Notebook):
    """A ttk Notebook with close buttons on each tab"""

    __initialized = False
    log = logging.getLogger(__name__)

    def __init__(self, *args, **kwargs):
        
        if not self.__initialized:
            self.__initialize_custom_style()
            self.__inititialized = True

        self.onclose = kwargs["onclose"]
        del kwargs["onclose"]
        kwargs["style"] = "CustomNotebook"
        ttk.Notebook.__init__(self, *args, **kwargs)

        self._active = None

        self.bind("<ButtonPress-1>", self.on_close_press, True)
        self.bind("<ButtonRelease-1>", self.on_close_release)

    def on_close_press(self, event):
        """Called when the button is pressed over the close button"""

        element = self.identify(event.x, event.y)

        if "close" in element:
            index = self.index("@%d,%d" % (event.x, event.y))
            self.state(['pressed'])
            self._active = index

    def on_close_release(self, event):
        """Called when the button is released over the close button"""
        if not self.instate(['pressed']):
            return

        element =  self.identify(event.x, event.y)
        index = self.index("@%d,%d" % (event.x, event.y))

        if "close" in element and self._active == index:
            #self.forget(index)
            #self.event_generate("<<NotebookTabClosed>>")
            tabname = self.tab(self.select(), "text")
            self.log.debug("Close tab: "+tabname)
            self.onclose(tabname)

        self.state(["!pressed"])
        self._active = None

    def __initialize_custom_style(self):
        """Initializes the custom style."""
        style = ttk.Style()
        self.images = (
            tk.PhotoImage("img_close", data='''
                R0lGODlhCAAIAMIBAAAAADs7O4+Pj9nZ2Ts7Ozs7Ozs7Ozs7OyH+EUNyZWF0ZWQg
                d2l0aCBHSU1QACH5BAEKAAQALAAAAAAIAAgAAAMVGDBEA0qNJyGw7AmxmuaZhWEU
                5kEJADs=
                '''),
            tk.PhotoImage("img_closeactive", data='''
                R0lGODlhCAAIAMIEAAAAAP/SAP/bNNnZ2cbGxsbGxsbGxsbGxiH5BAEKAAQALAAA
                AAAIAAgAAAMVGDBEA0qNJyGw7AmxmuaZhWEU5kEJADs=
                '''),
            tk.PhotoImage("img_closepressed", data='''
                R0lGODlhCAAIAMIEAAAAAOUqKv9mZtnZ2Ts7Ozs7Ozs7Ozs7OyH+EUNyZWF0ZWQg
                d2l0aCBHSU1QACH5BAEKAAQALAAAAAAIAAgAAAMVGDBEA0qNJyGw7AmxmuaZhWEU
                5kEJADs=
            ''')
        )

        style.element_create("close", "image", "img_close",
                            ("active", "pressed", "!disabled", "img_closepressed"),
                            ("active", "!disabled", "img_closeactive"), border=8, sticky='')
        style.layout("CustomNotebook", [("CustomNotebook.client", {"sticky": "nswe"})])
        style.layout("CustomNotebook.Tab", [
            ("CustomNotebook.tab", {
                "sticky": "nswe", 
                "children": [
                    ("CustomNotebook.padding", {
                        "side": "top", 
                        "sticky": "nswe",
                        "children": [
                            ("CustomNotebook.focus", {
                                "side": "top", 
                                "sticky": "nswe",
                                "children": [
                                    ("CustomNotebook.label", {"side": "left", "sticky": ''}),
                                    ("CustomNotebook.close", {"side": "left", "sticky": ''}),
                                ]
                            })
                        ]
                    })
                ]
            })
        ])









# called directly
if __name__ == '__main__':
    from globals import *
    raise NotCallableModuleError
    