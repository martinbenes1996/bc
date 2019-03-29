#!/usr/bin/env python3

"""
File:           main.py
Author:         Martin Benes
Institution:    Faculty of Information Technology
                Brno University of Technology

This module is the main, which is first to run.
Developed as a part of bachelor thesis "Counting of people using PIR sensor".
"""

import time

import app
import comm_mcast
import comm_serial
import model




def getReaderInstance(name, port=None):
    """Singleton Reader instance getter."""
    if name[0:2] == "S:":
        return comm_serial.Reader.getReader(name[2:])
    elif name[0:2] == "M:":
        return comm_mcast.Reader.getReader(name[2:])
    elif port:
        return comm_mcast.Reader.getReader(name, port)
    else:
        raise Exception("Unknown device type: "+name)
def getReader(name, port=None):
    """Reader callback getter."""
    return getReaderInstance(name, port).getSegment
def getRecorder(name, port=None):
    """Recorder callback getter."""
    return getReaderInstance(name, port).record


def main():
    """Main function."""

    # create sensor reader
    #s1 = comm_serial.Reader("/dev/ttyS3")
    m1 = comm_mcast.Reader.getReader("224.0.0.1", 1234)
    
    # create model
    m = model.Extractor(m1.indicate, m1.getSegment)
    
    # create window
    v = app.App.get()
    time.sleep(2)
    
    # connect callbacks
    v.getReader = getReader
    v.getRecorder = getRecorder

    # run main loop
    v.mainloop()
    



# main caller
if __name__ == "__main__":
    main()