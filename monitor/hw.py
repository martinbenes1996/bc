
import datetime
import serial
import _thread
import time
import sys


class Reader:
    readers = {}
    def __init__(self, devicename):
        self.devicename = devicename
        self.readers[self.devicename] = serial.Serial(devicename)
        self.segment = []
        self.segmentLock = _thread.allocate_lock()
        self.started = False
        self.mem = ''
        self.change = False
        self.setStatus = lambda _: None
        _thread.start_new_thread(self.read, ())

    def read(self):
        i = 0
        while True:
            i += 1
            s = self.readSegment()
            with self.segmentLock:
                self.segment = s
                self.indicate(True)
                #self.setStatus("Update received.")
                #print("Reader: Read ", i)
            self.started = True
            time.sleep(0.3)

    def readSegment(self):
        return [self.readSample() for _ in range(0,60)]

    def readSample(self):
        # read line
        l = ''
        if self.mem != '':
            l = self.mem
            self.mem = ''
        while l == '':
            l = self.readers[self.devicename].readline()[:-2]

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
    
    @classmethod
    def getReader(cls, name):
        if name not in cls.readers:
            return serial.Serial(name)
        else:
            return cls.readers[name]
    


    
        
