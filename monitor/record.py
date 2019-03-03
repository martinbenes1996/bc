
import json
import os
import _thread
import time

import sound

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
            self.count(m['delay'])
            time.sleep(m['delay'])
            # recording
            self.setMarked(i)
            
            if not os.path.exists('../data/'+self.session['name']+'/'):
                os.makedirs('../data/'+self.session['name']+'/')
            if m['signal']:
                self.signalRecorder('../data/'+self.session['name']+'/'+m['name']+'.csv')
            if m['cwt']:
                self.cwtRecorder('../data/'+self.session['name']+'/'+m['name'])
            self.beep()
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
    
    def count(self, secs):
        _thread.start_new_thread(self.count_run, (), {"secs" : secs})
    def count_run(self, secs=1):
        for i in range(0, secs):
            sound.sine_tone(1000, 200, 0.8)
            time.sleep(0.8)
    def beep(self):
        sound.sine_tone(440, 500)

    @classmethod
    def sine_tone(cls, frequency, duration, volume=1, sample_rate=22050):
        n_samples = int(sample_rate * duration)
        restframes = n_samples % sample_rate

        p = PyAudio()
        stream = p.open(format=p.get_format_from_width(1), # 8bit
                        channels=1, # mono
                        rate=sample_rate,
                        output=True)
        s = lambda t: volume * math.sin(2 * math.pi * frequency * t / sample_rate)
        samples = (int(s(t) * 0x7f + 0x80) for t in xrange(n_samples))
        for buf in izip(*[samples]*sample_rate): # write several samples at a time
            stream.write(bytes(bytearray(buf)))

        # fill remainder of frameset with silence
        stream.write(b'\x80' * restframes)

        stream.stop_stream()
        stream.close()
        p.terminate()

