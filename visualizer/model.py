
import comm as Comm
import _thread

class Model:
    def __init__(self):
        self.client = Comm.MCastClient()
        _thread.start_new_thread(self.actualize, ())
    
    def actualize(self):
        while True:
            data = self.client.receive()
            print("Model.actualize(): data")