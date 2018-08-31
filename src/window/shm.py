
import sys
import os
import ctypes

class Direction(ctypes.Structure):
     _fields_ = [("valid", ctypes.c_bool),
                ("azimuth", ctypes.c_int),
                ("value", ctypes.c_double),
                ("temperature", ctypes.c_double),
                ("probability", ctypes.c_double),
                ("score", ctypes.c_double)]

class Figure(ctypes.Structure):
     _fields_ = [("valid", ctypes.c_bool),
                ("azimuth", ctypes.c_int),
                ("distance", ctypes.c_double),
                ("temperature", ctypes.c_double),
                ("probability", ctypes.c_double),
                ("score", ctypes.c_double)]

class Bottles:
    def __init__(self, number):
        self._as_parameter_ = number

class ShmWrapper:
    def __init__(self):
        print("open shared memory")
        self.lib = ctypes.cdll.LoadLibrary('/home/martin/bc/src/libglobals.so')
        self.connectSharedMemory()
    def __del__(self):
        print("close shared memory")
        print("shmid", self.shmid)
        print("shm", self.shm)
        self.lib.closeSharedMemory(self.shmid, self.shm)
        
    def isShmCreated(self):
        return bool(self.lib.isShmCreated() % 2)
    def connectSharedMemory(self):
        self.shmid = self.lib.connectSharedMemory()
        self.shm = self.lib.allocateSharedMemory(self.shmid)