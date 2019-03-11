#!/usr/bin/env python3

import time

import comm
import comm_mcast
import comm_serial
import model
import view



def getReader(name, port=None):
    """Singleton Reader instance getter."""
    if name[0:2] == "S:":
        return comm_serial.Reader.getReader(name[2:])
    elif name[0:2] == "M:":
        return comm_mcast.Reader.getReader(name[2:])
    elif port:
        return comm_mcast.Reader.getReader(name, port)
    else:
        raise Exception("Unknown device type: "+name)

def getRecorder(name, port=None):
    """Recorder callback getter."""
    return getReader(name, port).record


def main():
    """Main function."""

    # create sensor reader
    #s1 = comm_serial.Reader("/dev/ttyS3")
    m1 = comm_mcast.Reader.getReader("224.0.0.1", 1234)
    
    # create model
    m = model.Extractor(m1.indicate, m1.getSegment)
    
    # create window
    v = view.App.get()

    time.sleep(2)
    
    # connect callbacks
    v.getReader = getReader
    v.getRecorder = getRecorder
    
    #v.readers["/dev/ttyS3"] = m1.getSegment
    #v.cwt["/dev/ttyS3"] = m.getBuffer
    
    #v.signalrecorders['/dev/ttyS3'] = s1.record
    #v.cwtrecorders['/dev/ttyS3'] = m.record
    #s1.setStatus = v.setStatus

    # run main loop
    v.mainloop()
    



# main caller
if __name__ == "__main__":
    main()