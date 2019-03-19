
import csv
import datetime
import numpy as np
import sys
import threading
import time

import comm
import conf


class Reader(comm.Reader):
    """Reader of data from file. Singleton.
    
    Attributes:
    """
    # socket instances
    _readers = {}
    @classmethod
    def getReader(cls, name):
        """Returns reader singleton instance.
        
        Arguments:
            name    Name of the file.
        """
        # return existing
        if name in cls._readers:
            return cls._readers[name]
        # instantiate
        else:
            cls._readers[name] = cls(name)
            return cls._readers[name]


    def __init__(self, name):
        """Constructs object.
        
        Arguments:
            name    Name of the file.    
        """
        super().__init__()
        # create variables
        self.name = name
        # start reader thread
        self.run()

    def run(self):
        self.readThrd = threading.Thread(target=self.read)
        self.readThrd.start()

    def read(self):
        """Reads segments from file. Done in separated thread."""
        for s in self.readSegment():
            with self.segmentLock:
                self.segment = s


    def readSegment(self):
        """Reads file and splits into segments. Generator."""
        with open(self.name, 'r') as f:
            rd = csv.reader(f)
            segmentN, overlap = conf.Config.segment()
            T = conf.Config.period()
            segment = []
            for line in rd:
                for sample in line:
                    # add sample to segment
                    segment.append( int(sample) )

                    # segment full
                    if len(segment) == segmentN:
                        #print("Comm_replay.Reader.read: segment received")
                        yield segment
                        segment = segment[-overlap:]
                        # record
                        self.write(segment)
                        # indicate change
                        self.indicate(True)
                        self.started = True
                        # sleep one period
                        time.sleep( T/1000. )
    
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
    
    @staticmethod
    def readFile(name):
        with open(name, 'r') as f:
            rd = csv.reader(f)
            return np.array([int(sample) for line in rd for sample in line])

    
        
