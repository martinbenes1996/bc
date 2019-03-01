
import json
import os
import _thread
import time

class Recorder:
    def __init__(self, signalRecorder, cwtRecorder):
        self.signalRecorder = signalRecorder
        self.cwtRecorder = cwtRecorder
        
        # run processing thread
        

    def start(self, session, setMarked, setDelayMarked):
        
        self.session = session
        self.setMarked, self.setDelayMarked = setMarked, setDelayMarked
        _thread.start_new_thread(self.run, ())

    def run(self):
        print("Record")
        for i,m in enumerate(self.session['measurements']):
            # delay
            self.setDelayMarked(i)
            time.sleep(m['delay'])
            # recording
            self.setMarked(i)
            
            if not os.path.exists('../data/'+self.session['name']+'/'):
                os.makedirs('../data/'+self.session['name']+'/')
            if m['signal']:
                self.signalRecorder('../data/'+self.session['name']+'/'+m['name']+'.csv')
            if m['cwt']:
                self.cwtRecorder('../data/'+self.session['name']+'/'+m['name'])
            time.sleep(m['time'])
            # stop recording
            if m['signal']:
                self.signalRecorder(None)
            if m['cwt']:
                self.cwtRecorder(None)

        self.setMarked( len(self.session['measurements']) )

    
    def generateSessionName(self):
        return "NewRecording"

    def saveSession(self, session):
        with open(session['name']+'.json', 'w') as f:
            json.dump(session, f)

    def loadSession(self, name):
        with open(name + '.json', 'r') as f:
            return json.loads(f.read())

