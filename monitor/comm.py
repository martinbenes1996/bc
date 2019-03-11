
import _thread

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
        """Getter of latest received data."""
        raise NotImplementedError
    
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
    


    
        
