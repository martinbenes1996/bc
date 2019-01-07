
import comm as Comm
import struct
import _thread

class Model:
    def __init__(self):
        self.client = Comm.MCastClient()
        _thread.start_new_thread(self.actualize, ())
    
    def actualize(self):
        while True:
            data = self.client.receive()
            azimuth, distance = struct.unpack('ii', data)
            print("Model.actualize(): data")
            print("Model.actualize(): azimuth", azimuth, "distance", distance)
