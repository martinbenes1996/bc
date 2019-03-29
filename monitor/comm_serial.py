

"""
File:           comm_serial.py
Author:         Martin Benes
Institution:    Faculty of Information Technology
                Brno University of Technology

This module contains classes enabling program to receive data from serial port.
Developed as a part of bachelor thesis "Counting of people using PIR sensor".
"""

import csv
import datetime
import serial
import _thread
import time
import sys

import comm


class Reader(comm.Reader):
    """Reader of data from serial port. Singleton.
    
    Attributes:
        readers         Reader instances for various serial ports.
        devicename      Name of the device.
        port            Serial file handle.
        mem             Buffer for error reading.
    """
    # reader instances
    readers = {}
    @classmethod
    def getReader(cls, name):
        """Returns reader singleton instance.
        
        Arguments:
            name    Name of serial port.
        """
        # instantiate
        if name not in cls.readers:
            return cls(name)
        # return existing
        else:
            return cls.readers[name]


    # Constructor
    def __init__(self, devicename):
        """Constructs object.
        
        Arguments:
            devicename
        """
        super().__init__()
        # create variables
        self.devicename = devicename
        self.mem = ''
        # check if singleton
        assert(self.devicename not in self.readers)
        # connect to serial port
        self.port = serial.Serial(devicename)
        self.readers[self.devicename] = self
        # start reader thread
        _thread.start_new_thread(self.read, ())

    # Data getter
    def getSegment(self):
        """Gets segment."""
        # reader not started
        if not self.started:
            raise Exception("Reader not started yet.")
        # multithread access
        with self.segmentLock:
            return self.segment
        

    def record(self, filename=None):
        """Controls recording.
        
        Arguments:
            filename    Filename of file to save recording to.
        """
        # filename not given or ""
        if not filename:
            # stop recording
            if self.filename:
                print("Recording to", self.filename, "ended.")
                self.filename = ''
                return
            # generate name
            filename = "PIR " + str(datetime.datetime.now()) + ".csv"
        # start recording
        self.filename = filename
        print("Recording to", self.filename, "started.")
        f = open(self.filename, 'w')


    def read(self):
        """Reads serial port. Done in separated thread."""
        i = 0
        while True:
            i += 1
            # read
            s = self.readSegment()
            with self.segmentLock:
                self.segment = s

            # record
            self.write(s)
            # indicate change
            self.indicate(True)
            self.started = True
            # wait 300 ms
            time.sleep(0.3)

    
    

    def write(self, segment):
        """Saves segment to file.
        
        Arguments:
            segment     Segment to save.
        """
        # recording turned off
        if not self.filename:
            return
        # save segment
        with open(self.filename, "a", newline='') as f:
            csvwriter = csv.writer(f)
            csvwriter.writerow(segment)


    def readSegment(self):
        """Reads segments sample by sample."""
        return [self.readSample() for _ in range(0,60)]

    def readSample(self):
        """Reads single sample."""
        # read line
        l = ''
        if self.mem != '':
            l = self.mem
            self.mem = ''
        while l == '':
            l = self.port.readline()[:-2]

        if len(l) > 3 and l[3] == b'\r':
            self.mem = l[4:]
            l = l[:3]

        # convert to int
        try:
            return int(l.decode('utf-8'))
        except Exception as e:
            return 0
    
    
    
    
    
    
    


    
 # called directly
if __name__ == '__main__':
    from globals import *
    raise NotCallableModuleError       
