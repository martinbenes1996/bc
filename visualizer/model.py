
import comm as Comm
import struct
import _thread

class Model:
    def __init__(self):
        self.client = Comm.MCastClient()
        self.objects = []
        _thread.start_new_thread(self.actualize, ())

    def actualize(self):
        while True:
            count, data = self.client.receive()
            
            print("Model.actualize():", count, "data received")
            print("Model.actualize():", data)

            self.objects = data
    
    def getObjects(self):
        return self.objects