
import _thread

class Recorder:
    def __init__(self, signalRecorder, cwtRecorder):
        self.signalRecorder = signalRecorder
        self.cwtRecorder = cwtRecorder
        
        # run processing thread
        

    def start(self):
        print("Record")
        #_thread.start_new_thread(self.run, ())

    def run(self):
        pass


    
    def generateSessionName(self):
        return "NewRecording"

    def saveSession(self, name, session):
        pass
        # save session to file

    def loadSession(self, name):
        # read session from file
        return {}

