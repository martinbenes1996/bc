

"""
File:           comm.py
Author:         Martin Benes
Institution:    Faculty of Information Technology
                Brno University of Technology

This module contains interface for data reading.
Developed as a part of bachelor thesis "Counting of people using PIR sensor".
"""

import logging
import sys
import threading

import conf


class Reader:
    """Interface to read data.
    
    Attributes:
        started         Whether reading of source started.
        segment         Shared buffer for last received segment.
        segmentLock     Lock for simultaneous access to segment buffer.
        change          Change indicator.
        filename        Filename of file Reader records to. Not recording if empty.
    """
    log = logging.getLogger(__name__)

    @classmethod
    def getReader(cls, name, port=None):
        """Singleton Reader instance getter."""
        raise NotImplementedError


    def __init__(self):
        """Constructor."""
        self.started = False
        self.segment = []
        self.segmentLock = threading.Lock()
        self.change = False
        self.filename = ""
    
    def record(self, filename=""):
        """Record read segments to filename.
        
        Arguments:
            filename        File to record to. If empty and recording, stop recording.
                            If empty and not recording, record to file with default name.
        """
        raise NotImplementedError

    def getSegment(self):
        """Gets segment."""
        # reader not started
        if not self.started:
            self.log.info("No data received.")
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
    





# called directly
if __name__ == '__main__':
    from globals import *
    raise NotCallableModuleError
    
    