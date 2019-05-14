
import sys

import tkinter as tk

sys.path.insert(0, '.')
import conf
import views



def main():
    conf.Config.setDebug(False)
    sm = views.SerialView(tk.Tk())
    sm.begin(lambda _ : None, lambda _ : None)


if __name__ == '__main__':
    main()

