#!/usr/bin/env python3

import time

import hw
import model
import view





def main():
    """Main function."""

    # create sensor reader
    s1 = hw.Reader("/dev/ttyS3")
    
    # create model
    m = model.Extractor(s1.indicate, s1.getSegment)
    
    # create window
    v = view.App.get()

    time.sleep(2)
    
    # connect callbacks
    v.readers["/dev/ttyS3"] = s1.getSegment
    v.cwt["/dev/ttyS3"] = m.getBuffer
    v.signalrecorders['/dev/ttyS3'] = s1.record
    v.cwtrecorders['/dev/ttyS3'] = m.record
    s1.setStatus = v.setStatus

    # run main loop
    v.mainloop()
    



# main caller
if __name__ == "__main__":
    main()