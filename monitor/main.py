#!/usr/bin/env python3

import hw
import model
import view




def main():
    # create sensor reader
    s1 = hw.Reader("/dev/ttyS3")
    # create model
    m = model.Extractor(s1.indicate, s1.getSegment)
    # create window
    v = view.App.get()
    # connect callbacks
    v.readers["/dev/ttyS3"] = s1.getSegment
    v.cwt["/dev/ttyS3"] = m.getBuffer
    s1.setStatus = v.setStatus

    v.mainloop()
    



if __name__ == "__main__":
    main()