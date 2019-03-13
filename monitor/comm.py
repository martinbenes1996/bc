
import sys
import _thread
sys.path.insert(0, '../collector-py/')
import conf

class Reader:
    """Interface to read data."""

    def __init__(self):
        """Constructor."""
        self.started = False
        self.segment = []
        self.segmentLock = _thread.allocate_lock()
        self.change = False
        self.filename = ""
    
    def record(self, filename=""):
        """Record read segments to filename."""
        raise NotImplementedError

    def getSegment(self):
        """Gets segment."""
        # reader not started
        if not self.started:
            print("No data received.", file=sys.stderr)
            segmentN = conf.Config.segment()[0]
            return [0 for _ in range(0,segmentN)]
        # multithread access
        with self.segmentLock:
            return self.segment
    
    def indicate(self, swapper):
        """Indicates new data in style of Test&Set.
        
        Arguments:
            swapper     Must be False.
        """
        s = self.change
        self.change = bool(swapper)
        return s
    
    @classmethod
    def getReader(cls, name, port=None):
        """Singleton Reader instance getter."""
        raise NotImplementedError
    


    
        
