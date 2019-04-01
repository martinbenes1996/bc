

"""
File:           conf.py
Author:         Martin Benes
Institution:    Faculty of Information Technology
                Brno University of Technology

This module contains global configuration of the program.
Developed as a part of bachelor thesis "Counting of people using PIR sensor".
"""

import json
import numpy as np

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

    # configuration instance
    uniqueConf = None
    def get(cls):
        """Configuration getter. Instantiates, if not instantiated yet."""
        # instantiate
        if not cls.uniqueConf:
            cls.uniqueConf = cls.ConfigSingleton()
        # return existing
        return cls.uniqueConf
    
    @classmethod
    def segment(cls):
        """Returns segment informations (N, overlap)."""
        return cls.get(cls).samples, cls.get(cls).overlap
    
    @classmethod
    def fs(cls):
        """Returns sampling frequency deduced from other attributes."""
        N,overlap = cls.segment()
        sendPeriod = cls.period()
        return (N-overlap) * (1000/sendPeriod)

    @classmethod
    def period(cls):
        """Returns sending period."""
        return cls.get(cls).period
    
    @classmethod
    def channel(cls):
        """Returns multicast channel informations (IP, port)."""
        return (cls.get(cls).channel_address, cls.get(cls).channel_port)




# called directly
if __name__ == '__main__':
    from globals import *
    raise NotCallableModuleError
    