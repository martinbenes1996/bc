
import sys
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

        _thread.start_new_thread(self.process, ())

    def process(self):
        while True:
            if self.indicate(False):
                b = self.engine.process( self.getData() )
                with self.bufferLock:
                    self.buffer = b
    
    def getBuffer(self):
        with self.bufferLock:
            return self.buffer


