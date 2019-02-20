
import csv
import datetime
import serial
import _thread
import time
import sys


class Reader:
    """Reader of data from serial port. Singleton.
    
    Attributes:
        readers     Reader instances for various serial ports.
        devicename
        segment
        segmentLock
        started
        mem
        filename
        change
        setStatus
    """
    # reader instances
    readers = {}

    def __init__(self, devicename):
        """Constructs object.
        
        Arguments:
            devicename
        """
        # create variables
        self.devicename = devicename
        self.segment = []
        self.segmentLock = _thread.allocate_lock()
        self.started = False
        self.mem = ''
        self.filename = ""
        self.change = False
        self.setStatus = lambda _: None
        # check if singleton
        assert(self.devicename not in self.readers)
        # connect to serial port
        self.readers[self.devicename] = serial.Serial(devicename)
        # start reader thread
        _thread.start_new_thread(self.read, ())

    def read(self):
        """Reads serial port. Done in separated thread."""
        i = 0
        while True:
            i += 1
            # read
            s = self.readSegment()
            with self.segmentLock:
                self.segment = s
                #self.setStatus("Update received.")
                #print("Reader: Read ", i)

            # record
            self.write(s)
            # indicate change
            self.indicate(True)
            self.started = True
            # wait 300 ms
            time.sleep(0.3)
    
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
            l = self.readers[self.devicename].readline()[:-2]

        if len(l) > 3 and l[3] == b'\r':
            self.mem = l[4:]
            l = l[:3]

        # convert to int
        try:
            return int(l.decode('utf-8'))
        except Exception as e:
            #print(l)
            #print(e)
            return 0
        # convert to bytes
        #return (i).to_bytes(2, byteorder='big')
    
    def getSegment(self):
        """Gets segment."""
        # reader not started
        if not self.started:
            raise Exception("Reader not started yet.")
        # multithread access
        with self.segmentLock:
            return self.segment
    
    def indicate(self, swapper):
        """Indicates new data in style of Test&Set.
        
        Arguments:
            swapper     Must be False.
        """
        # swap and return
        s = self.change
        self.change = bool(swapper)
        return s
    
    @classmethod
    def getReader(cls, name):
        """Returns reader singleton instance.
        
        Arguments:
            name    Name of serial port.
        """
        # instantiate
        if name not in cls.readers:
            return serial.Serial(name)
        # return existing
        else:
            return cls.readers[name]
    


    
        
