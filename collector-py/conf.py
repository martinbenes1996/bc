
import json
import numpy as np

class Config:
    class ConfigSingleton:
        def __init__(self):
            with open('../module/comm.conf.json', 'r') as f:
                data = json.loads(f.read())
            self.period = data["period"]
            self.samples = data["segment"]["samples"]
            self.overlap = data["segment"]["overlap"]

            self.cwtcoefs = np.arange(1,4,0.05)

            self.channel_address = data["channel"]["address"]
            self.channel_port = data["channel"]["port"]

            print("Config read.")
            print(self.samples, "samples,", self.overlap, "overlap,", self.period, "period")

    uniqueConf = None
    def get(cls):
        if not cls.uniqueConf:
            cls.uniqueConf = cls.ConfigSingleton()
        return cls.uniqueConf
    
    @classmethod
    def segment(cls):
        return cls.get(cls).samples, cls.get(cls).overlap
    
    @classmethod
    def period(cls):
        return cls.get(cls).period
    
    @classmethod
    def cwtCoefs(cls):
        return cls.get(cls).cwtcoefs
    
    @classmethod
    def channel(cls):
        return (cls.get(cls).channel_address, cls.get(cls).channel_port)