
import sys

import tkinter as tk

sys.path.insert(0, '.')
import views



def main():
    sm = views.SerialView(tk.Tk())
    sm.begin(lambda _ : None, lambda _ : None)


if __name__ == '__main__':
    main()

