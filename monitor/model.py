
import datetime
import sys
import time
import _thread

sys.path.insert(0, '../collector-py/')
import cwt


class Extractor:
    def __init__(self, indicate, source):
        self.indicate = indicate
        self.getData = source

        self.engine = cwt.Transformer()
        
        self.buffer = []
        self.bufferLock = _thread.allocate_lock()

        self.filename = ''

        _thread.start_new_thread(self.process, ())

    def process(self):
        while True:
            if self.indicate(False):
                b = self.engine.process( self.getData() )
                with self.bufferLock:
                    self.buffer = b
            else:
                time.sleep(0.1)
    
    def getBuffer(self):
        with self.bufferLock:
            return self.buffer
    
    def record(self, name=None):
        if not name:
            if self.filename:
                print("Recording to", self.filename, "ended.")
                self.filename = ''
                return
            name = "CWT " + str(datetime.datetime.now()) + ".dat"
        self.filename = name
        print("Recording to", self.filename, "started.")
        f = open(self.filename, 'w')
    def write(self, data):
        pass


