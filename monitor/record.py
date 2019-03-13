
import json
import os
import _thread
import time

import tkinter as tk
from tkinter import ttk


class Recorder:
    def __init__(self, signalRecorder):
        self.signalRecorder = signalRecorder
        
        

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
            self.beep()
            time.sleep(m['time'])
            # stop recording
            if m['signal']:
                self.signalRecorder(None)

        self.setMarked( len(self.session['measurements']) )

    
    def generateSessionName(self):
        return "NewRecording"

    def saveSession(self, session):
        with open("sessions/"+session['name']+'.json', 'w') as f:
            json.dump(session, f)

    def loadSession(self, name):
        with open("sessions/"+name + '.json', 'r') as f:
            return json.loads(f.read())
    
    def count(self, secs):
        _thread.start_new_thread(self.count_run, (), {"secs" : secs})
    def count_run(self, secs=1):
        for i in range(0, secs):
            self.sine_tone(1000, 200, 0.8)
            time.sleep(0.8)
    def beep(self):
        self.sine_tone(440, 500)

    @classmethod
    def sine_tone(frequency, duration, volume=1, sample_rate=22050):
        os.system("pwd")
        os.system("echo $USER")
        os.system("./beep.sh "+str(frequency)+" "+str(duration))


class View:
    class MemFunction:
        def __init__(self, f, arg1):
            self.f = f
            self.arg1 = arg1
        def __call__(self):
            self.f(self.arg1)

    def __init__(self, root, setRecording):
        self.root = root
        self.measurements = []
        self.setRecording = setRecording
    
    def begin(self, source, recordCallback):
        self.recorder = Recorder(recordCallback)
        self.measurements = []
        self.setRecording(True)

        self.recordFrame = tk.Frame(self.root, highlightcolor='black', highlightbackground='black', highlightthickness=3, bd=0)
        self.recordFrame.grid(row=0, column=3, rowspan=100, sticky=tk.N+tk.S+tk.E)
        self.headerFrame = tk.Label(self.recordFrame, text=u"Recording: "+source, font=30).grid(row=0, column=0, sticky=tk.N+tk.W)
        self.closeRecord = tk.Button(self.recordFrame, text="Close", command=self.endRecordingSession).grid(row=0, column=1, sticky=tk.N+tk.E)

        self.sessionName = tk.Text(self.recordFrame, height=1, width=40)
        self.sessionName.insert(tk.INSERT, self.recorder.generateSessionName())
        self.sessionName.grid(columnspan=2, sticky=tk.N+tk.W)

        self.recordBtn = tk.Button(self.recordFrame, text="Record", command=self.startRecording)
        self.recordBtn.grid(columnspan=2, sticky=tk.N+tk.E+tk.W)

        self.loadBtn = tk.Button(self.recordFrame, text="Load from file", command=self.loadSession)
        self.loadBtn.grid(columnspan=2, sticky=tk.N+tk.E+tk.W)
        self.addBtn = tk.Button(self.recordFrame, text="Add measurement", command=self.addMeasurement)
        self.addBtn.grid(columnspan=2, sticky=tk.N+tk.E+tk.W)
        self.saveBtn = tk.Button(self.recordFrame, text="Save to file", command=self.saveSession)
        self.saveBtn.grid(columnspan=2, sticky=tk.N+tk.E+tk.W)
    
    def endRecordingSession(self):
        del self.recorder
        for m in self.measurements:
            del m
        self.measurements = []
        self.recordFrame.destroy()
        del self.recordFrame
        self.setRecording(False)
    def startRecording(self):
        self.recordBtn.config(text='Stop Recording', command=self.stopRecording)
        self.recordFrame.config(highlightcolor='red', highlightbackground='red')
        self.recorder.start(self.getSession(), self.recordSlave_markMeasurement, self.recordSlave_markDelay)
    def recordSlave_unmarkAll(self):
        for m in self.measurements:
            m['delayFrame'].config(highlightcolor='black', highlightbackground='black')
            m['frame'].config(highlightcolor='black', highlightbackground='black')
    def recordSlave_markMeasurement(self, i):
        self.recordSlave_unmarkAll()
        if i == len(self.measurements):
            return
        self.measurements[i]['frame'].config(highlightcolor='red', highlightbackground='red')
    def recordSlave_markDelay(self, i):
        self.recordSlave_unmarkAll()
        if i == len(self.measurements):
            return
        self.measurements[i]['delayFrame'].config(highlightcolor='red', highlightbackground='red')
    def stopRecording(self):
        self.recordBtn.config(text='Record', command=self.startRecording)
        self.recordFrame.config(highlightcolor='black', highlightbackground='black')
    def addMeasurement(self, value = {'name' : '', 'time' : 5, 'delay' : 10, 'signal' : True}):
        self.addBtn.grid_forget()
        self.saveBtn.grid_forget()

        measurement = {}

        measurement['delayFrame'] = tk.Frame(self.recordFrame, highlightcolor='black', highlightbackground='black', highlightthickness=1, bd=0)
        tk.Label(measurement['delayFrame'], text=u"Delay [s]:").grid(sticky=tk.W)
        measurement['delay'] = tk.Text(measurement['delayFrame'], height=1, width=20)
        measurement['delay'].insert(tk.INSERT, str(value['delay']))
        measurement['delay'].grid(row=2, column=1, columnspan=2, sticky=tk.W+tk.N)
        measurement['delayFrame'].grid(columnspan=2, sticky=tk.N)

        measurement['frame'] = tk.Frame(self.recordFrame, highlightcolor='black', highlightbackground='black', highlightthickness=1, bd=0)
        measurement['frame'].grid(columnspan=2, sticky=tk.N)

        tk.Label(measurement['frame'], text=u"Measurement", font=25).grid(row=0, column=0, sticky=tk.N+tk.W)

        measurement['close'] = tk.Button(measurement['frame'], text="X", command=self.MemFunction(self.deleteMeasurement,len(self.measurements)))
        measurement['close'].grid(row=0, column=2, sticky=tk.E+tk.N)

        tk.Label(measurement['frame'], text=u"Name:").grid(sticky=tk.W)
        measurement['name'] = tk.Text(measurement['frame'], height=1, width=20)
        measurement['name'].insert(tk.INSERT, value['name'])
        measurement['name'].grid(row=1, column=1, sticky=tk.W+tk.N)        

        tk.Label(measurement['frame'], text=u"Length [s]:").grid(sticky=tk.W)
        measurement['time'] = tk.Text(measurement['frame'], height=1, width=20)
        measurement['time'].insert(tk.INSERT, str(value['time']))
        measurement['time'].grid(row=2, column=1, columnspan=2, sticky=tk.W+tk.N)

        measurement['signalVal'] = tk.IntVar()
        measurement['signalVal'].set( int(value['signal']) )

        measurement['signal'] = ttk.Checkbutton(measurement['frame'], text="Signal", variable=measurement['signalVal'])
        measurement['signal'].grid(row=3, column=1, columnspan=2, sticky=tk.W+tk.N)
        
        self.measurements.append(measurement)


        self.addBtn.grid(columnspan=2, sticky=tk.N+tk.E+tk.W)
        self.saveBtn.grid(columnspan=2, sticky=tk.N+tk.E+tk.W)

    def deleteMeasurement(self, index):
        self.measurements[index]['delayFrame'].destroy()
        self.measurements[index]['frame'].destroy()
        del self.measurements[index]

        for i,m in enumerate(self.measurements):
            m['close'].config(command=self.MemFunction(self.deleteMeasurement, i))

    def loadSession(self):
        filename = self.sessionName.get("1.0","end-1c")

        session = self.recorder.loadSession(filename)

        self.sessionName.delete('1.0', tk.END)
        self.sessionName.insert(tk.INSERT, session['name'])
        for _ in self.measurements:
            self.deleteMeasurement(0)
        for it in session['measurements']:
            self.addMeasurement(it)

    
    def getSession(self):
        session = {'measurements' : []}

        session['name'] = self.sessionName.get("1.0","end-1c")
        print("Save session", session['name'])
        
        for m in self.measurements:
            d = {}
            d['delay'] = int(m['delay'].get("1.0", "end-1c"))
            d['name'] = m['name'].get("1.0","end-1c")
            d['time'] = int(m['time'].get("1.0", "end-1c"))
            d['signal'] = bool(m['signal'].state())
            session['measurements'].append(d)
        return session

    def saveSession(self):
        self.recorder.saveSession(self.getSession())
