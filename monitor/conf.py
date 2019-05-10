

"""
File:           conf.py
Author:         Martin Benes
Institution:    Faculty of Information Technology
                Brno University of Technology

This module contains global configuration of the program.
Developed as a part of bachelor thesis "Counting of people using PIR sensor".
"""

import json
import logging
import signal
import numpy as np

import globals

class Config:
    """Includes global configuration for the whole program read from file.
    
    Attributes:
        uniqueConf          Unique configuration.
    """
    class ConfigSingleton:
        """Reads configuration file. Only one instance exists in the system (singleton).
        
        Attributes:
            period              Period of receiving.
            samples             Segment size.
            overlap             Overlap of segments.
            channel_address     Multicast channel address.
            channel_port        Multicast channel port.
        """
        
        def __init__(self):
            """Constructor for configuration. Reads configuration file."""
            with open('../module/comm.conf.json', 'r') as f:
                data = json.loads(f.read())
            self.period = data["period"]
            self.samples = data["segment"]["samples"]
            self.overlap = data["segment"]["overlap"]

            self.channel_address = data["channel"]["address"]
            self.channel_port = data["channel"]["port"]

            # initialize logging
            logging.basicConfig(format='%(levelname)s\t%(name)s: %(funcName)s(): %(lineno)i: %(message)s', level=logging.DEBUG)
            logging.getLogger('matplotlib').setLevel(logging.WARNING)

            # initialize signal handlers
            def signal_handler(signal,frame):
                globals.quit = True
            signal.signal(signal.SIGINT, signal_handler)

    # configuration instance
    uniqueConf = None
    @classmethod
    def get(cls):
        """Configuration getter. Instantiates, if not instantiated yet."""
        # instantiate
        if not cls.uniqueConf:
            cls.uniqueConf = cls.ConfigSingleton()
        # return existing
        return cls.uniqueConf
    @classmethod
    def init(cls):
        cls.get()
    
    @classmethod
    def segment(cls):
        """Returns segment informations (N, overlap)."""
        return cls.get().samples, cls.get().overlap
    
    @classmethod
    def fs(cls):
        """Returns sampling frequency deduced from other attributes."""
        N,overlap = cls.segment()
        sendPeriod = cls.period()
        return (N-overlap) * (1000/sendPeriod)

    @classmethod
    def period(cls):
        """Returns sending period."""
        return cls.get().period
    
    @classmethod
    def channel(cls):
        """Returns multicast channel informations (IP, port)."""
        return (cls.get().channel_address, cls.get().channel_port)



Config.init()

# called directly
if __name__ == '__main__':
    from globals import *
    raise NotCallableModuleError
    