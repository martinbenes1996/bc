
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
        #os.environ['LD_LIBRARY_PATH'] = '../'
        self.shm = ctypes.cdll.LoadLibrary('/home/martin/bc/src/libglobals.so')
        print(self.isInitialized())
        if not self.isInitialized():
            print("Shared memory not initialized.", file=sys.stderr)
            exit(1)
        
    def isInitialized(self):
        return bool(self.shm.isInitialized() % 2)