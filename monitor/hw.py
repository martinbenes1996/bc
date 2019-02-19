
import datetime
import serial
import _thread
import time
import sys


class Reader:
    def __init__(self, devicename):
        self.device = serial.Serial(devicename)
        self.segment = []
        self.segmentLock = _thread.allocate_lock()
        self.started = False
        self.mem = ''
        self.change = False
        _thread.start_new_thread(self.read, ())

    def read(self):
        i = 0
        while True:
            i += 1
            s = self.readSegment()
            with self.segmentLock:
                self.segment = s
                self.indicate(True)
                #print("Reader: Read ", i)
            self.started = True

    def readSegment(self):
        return [self.readSample() for _ in range(0,60)]

    def readSample(self):
        # read line
        l = ''
        if self.mem != '':
            l = self.mem
            self.mem = ''
        while l == '':
            l = self.device.readline()[:-2]

        if len(l) > 3 and l[3] == b'\r':
            self.mem = l[4:]
            l = l[:3]

        # convert to int
        try:
            return int(l.decode('utf-8'))
        except Exception as e:
            print(l)
            print(e)
            return 0
        # convert to bytes
        #return (i).to_bytes(2, byteorder='big')
    
    def getSegment(self):
        if not self.started:
            raise Exception("Reader not started yet.")
        with self.segmentLock:
            return self.segment
    
    def indicate(self, swapper):
        s = self.change
        self.change = swapper
        return s
    


    
        
