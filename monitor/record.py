

"""
File:           record.py
Author:         Martin Benes
Institution:    Faculty of Information Technology
                Brno University of Technology

This module contains classes performing recording session.
Developed as a part of bachelor thesis "Counting of people using PIR sensor".
"""


import json
import os
import threading
import time

import tkinter as tk
from tkinter import ttk


class Recorder:
    """Recorder representation.
    
    Attributes:
        signalRecorder          Callback for record the signal.
    """

    def __init__(self, signalRecorder):
        """Constructor of Recorder.
        
        Arguments:
            signalRecorder      Callback for record the signal.
        """
        self.signalRecorder = signalRecorder    

    def start(self, session, setMarked, setDelayMarked):
        """Programs the recording session and runs it in separate thread.
        
        Arguments:
            session             Session, exported from view.
            setMarked           Callback for marking.
            setDelayMarked      Callback for delay of marking.
        """
        self.session = session
        self.setMarked, self.setDelayMarked = setMarked, setDelayMarked
        threading.Thread(target=self.run).start()

    def run(self):
        """Runs the recording session."""
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
        """Generates a name for session name."""
        return "NewRecording"

    def saveSession(self, session):
        """Save the session in the file.
        
        Arguments:
            session     Session state to save.
        """
        with open("sessions/"+session['name']+'.json', 'w') as f:
            json.dump(session, f)

    def loadSession(self, name):
        """Load the session from the file.
        
        Arguments:
            name        Name of the file.
        """
        with open("sessions/"+name + '.json', 'r') as f:
            return json.loads(f.read())
    
    def count(self, secs):
        """Signalizes number of seconds.
        
        Arguments:
            secs        Count of seconds to signalize.
        """
        _thread.start_new_thread(self.count_run, (), {"secs" : secs})
    def count_run(self, secs=1):
        """Beep for length.
        
        Arguments:
            secs        Length of beeping.
        """
        for i in range(0, secs):
            self.sine_tone(1000, 0.2, 0.8)
            time.sleep(0.8)
    def beep(self):
        """Beeps."""
        self.sine_tone(440, 0.5)

    @classmethod
    def sine_tone(cls, frequency, duration, volume=1, sample_rate=22050):
        """Beeps.
        
        Arguments:
            frequency       Frequency of beep.
            duration        Duration of beep in ms.
            volume          Volume of beep.
            sample_rate     Sample rate.
        """
        os.system("bash beep.sh "+str(frequency)+" "+str(duration))


class View:
    """RecordView.
    
    Attributes:
        root            Parent view element.
        measurements    List of measurements.
        setRecording    Callback to set record.
        recordFrame     Main frame.
        headerFrame     Frame for header.
        closeRecord     Button to close recording view.
        sessionName     Input with session name.
        recordBtn       Button to start recording session.
        loadBtn         Button to load session.
        addBtn          Button to add new measurement.
        saveBtn         Button to save session.
    """

    class MemFunction:
        """Function with static variable.
        
        Attributes:
            f       Callable to call.
            arg1    Argument to handle.
        """
        def __init__(self, f, arg1):
            """Constructor of function with static variable.
            
            Arguments:
                f       Callable to call.
                arg1    Argument to handle.
            """
            self.f = f
            self.arg1 = arg1
        def __call__(self):
            """Call the function."""
            self.f(self.arg1)

    def __init__(self, root, setRecording):
        """Constructor of the RecordView.
        
        Arguments:
            root            Parent view element.
            setRecording    Callback to set record.
        """
        self.root = root
        self.measurements = []
        self.setRecording = setRecording
    
    def begin(self, source, recordCallback):
        """Creates the recording view.  
        
        Arguments:
            source          Source of recording.
            recordCallback  Callback for recording.
        """
        self.recorder = Recorder(recordCallback)
        self.measurements = []
        self.setRecording(True)

        self.recordFrame = tk.Frame(self.root, highlightcolor='black', highlightbackground='black', highlightthickness=3, bd=0)
        self.recordFrame.grid(row=0, column=3, rowspan=100, sticky=tk.N+tk.S+tk.E)
        if len(source) > 15:
            titletext = u"Recording: ..."+source[-15:]
        else:
            titletext = u"Recording: "+source
        self.headerFrame = tk.Label(self.recordFrame, text=titletext, font=30).grid(row=0, column=0, sticky=tk.N+tk.W)
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
        """Closes the Recordview."""
        del self.recorder
        for m in self.measurements:
            del m
        self.measurements = []
        self.recordFrame.destroy()
        del self.recordFrame
        self.setRecording(False)
    def startRecording(self):
        """Handler of event to start recording."""
        self.recordBtn.config(text='Stop Recording', command=self.stopRecording)
        self.recordFrame.config(highlightcolor='red', highlightbackground='red')
        self.recorder.start(self.getSession(), self.recordSlave_markMeasurement, self.recordSlave_markDelay)
    def recordSlave_unmarkAll(self):
        """Unmarks all frames."""
        for m in self.measurements:
            m['delayFrame'].config(highlightcolor='black', highlightbackground='black')
            m['frame'].config(highlightcolor='black', highlightbackground='black')
    def recordSlave_markMeasurement(self, i):
        """Marks measurement frame.
        
        Arguments:
            i       Index of measurement frame.
        """
        self.recordSlave_unmarkAll()
        if i == len(self.measurements):
            return
        self.measurements[i]['frame'].config(highlightcolor='red', highlightbackground='red')
    def recordSlave_markDelay(self, i):
        """Marks delay frame.
        
        Arguments:
            i       Index of delay frame.
        """
        self.recordSlave_unmarkAll()
        if i == len(self.measurements):
            return
        self.measurements[i]['delayFrame'].config(highlightcolor='red', highlightbackground='red')
    def stopRecording(self):
        """Stops the recording."""
        self.recordBtn.config(text='Record', command=self.startRecording)
        self.recordFrame.config(highlightcolor='black', highlightbackground='black')
    def addMeasurement(self, value = {'name' : '', 'time' : 5, 'delay' : 10, 'signal' : True}):
        """Adds new measurement to the session.
        
        Arguments:
            value       Values for the measurement.
        """
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
        """Deletes the measurement.
        
        Arguments:
            index       Index of measurement to delete.
        """
        self.measurements[index]['delayFrame'].destroy()
        self.measurements[index]['frame'].destroy()
        del self.measurements[index]

        for i,m in enumerate(self.measurements):
            m['close'].config(command=self.MemFunction(self.deleteMeasurement, i))

    def loadSession(self):
        """Loads a session."""
        filename = self.sessionName.get("1.0","end-1c")

        session = self.recorder.loadSession(filename)

        self.sessionName.delete('1.0', tk.END)
        self.sessionName.insert(tk.INSERT, session['name'])
        for _ in self.measurements:
            self.deleteMeasurement(0)
        for it in session['measurements']:
            self.addMeasurement(it)
    
    def getSession(self):
        """Constructs new measurement."""
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
        """Saves the session to file."""
        self.recorder.saveSession(self.getSession())






# called directly
if __name__ == '__main__':
    from globals import *
    raise NotCallableModuleError
    