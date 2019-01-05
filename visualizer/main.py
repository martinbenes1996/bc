#!/usr/bin/env python3

import view
import model


def main():
    m = model.Model()
    v = view.App.get()
    v.mainloop()

if __name__ == '__main__':
    main()