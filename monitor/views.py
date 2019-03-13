
import os
import re

import tkinter as tk

import comm_serial
import ui

class SerialMenu:
    def __init__(self, root):
        self.root = root
        self.serials = []

    def begin(self, create, close):
        # look up serials
        allfiles = re.findall(r'ttyS[0-9]+', ",".join(os.listdir("/dev/")))
        # sort serial files by numeric appendix numerically
        serialfiles = sorted(allfiles, key=self.sortByNumericAppendix)
        # headline
        tk.Label(self.root, text=u"Ports", font=30).grid(column=0, sticky=tk.W+tk.S, padx=30)

        # generate checkbutons
        for f in serialfiles:
            checkbutton = ui.CheckButton(self.root, "S:/dev/" + f)
            checkbutton.checked, checkbutton.unchecked = create, close
            checkbutton.alive = comm_serial.Reader.getReader
            checkbutton.button.grid(column=0, sticky=tk.W+tk.S, padx=30)
            checkbutton.run()
            self.serials.append(checkbutton)
    
    def disable(self):
        for chb in self.serials:
            chb.disable()
    def update(self):
        for chb in self.serials:
            chb.manualUpdate()
        

    @staticmethod
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





        


