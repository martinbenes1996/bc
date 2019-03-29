

"""
File:           model.py
Author:         Martin Benes
Institution:    Faculty of Information Technology
                Brno University of Technology

This module contains the classes, controlling the extraction and classification.
Developed as a part of bachelor thesis "Counting of people using PIR sensor".
"""

import json
import numpy as np
import sys

import fuzzy
import segment

# to delete
import datetime
import time
import _thread
sys.path.insert(0, '../collector-py/')
import cwt

class Extractor:
    """Adapter of CWT in monitor from collector.
    
    Attributes:
        indicate    Callback to indicate update in style of Test&Set.
        getData     Callback for getting data.
        engine      Engine to perform CWT from collector.
        buffer      Buffer to save CWT result in.
        filename    Filename of file to save recorded signal to.
    """
    def __init__(self, indicate, source):
        """Constructs object.
        
        Arguments:
            indicate    Callback to indicate update in style of Test&Set.
            source      Callback for getting data.
        """
        # create variables
        self.indicate = indicate
        self.getData = source
        self.filename = ''
        self.buffer = []
        self.bufferLock = _thread.allocate_lock()
        # connect to collector
        self.engine =  cwt.Transformer()

        # run processing thread
        _thread.start_new_thread(self.process, ())

    def process(self):
        """Processes data to CWT. Main for separated thread."""
        while True:
            # if changed
            if self.indicate(False):
                # CWT
                b = self.engine.process( self.getData() )
                with self.bufferLock:
                    self.buffer = b
                self.write(b)
            # wait 100 ms
            else:
                time.sleep(0.1)
    
    def getBuffer(self):
        """Returns buffer."""
        # multithread access
        with self.bufferLock:
            return self.buffer
    
    def record(self, name=None):
        """Controls recording.
        
        Arguments:
            name    Name of file to save recording to.
        """
        # name not given or empty string
        if not name:
            # end recording
            if self.filename:
                print("Recording to", self.filename, "ended.")
                self.filename = ''
                return
            # generate name
            name = "CWT " + str(datetime.datetime.now()) + ".dat"
        # start recording
        self.filename = name
        print("Recording to", self.filename, "started.")
        f = open(self.filename, 'w')

    def write(self, data):
        """Write data to file.
        
        Arguments:
            data        Data to save.
        """
        # recording switched off
        if not self.filename:
            return
        # save
        pass
    
    @staticmethod
    def extract(x):
        artefacts = segment.Artefact.parseArtefacts(x)
        return [a.getFeatures() for a in artefacts]


# to document

class Classification:
    def __init__(self, featureDimension, areaSize):
        self.rows,self.columns = areaSize
        self.area = [[0 for _ in range(self.columns)] for _ in range(self.rows)]
        self.classifiers = {}
        self.classifiers['distance'] = LinearRegression(featureDimension)
        self.classifiers['center'] = LinearRegression(featureDimension)
        self.classifiers['right'] = LinearRegression(featureDimension)
        self.allKeys = {'distance','center','right'}

    def train(self, x, key={'distance': True, 'center': True, 'right': True}):
        assert(key.keys() <= self.allKeys)
        for k in (self.allKeys - key.keys()):
            key[k] = True
        for k,v in key.items():
            self.classifiers[k].addTrainData(x,v)
    
    def load(self, filename):
        with open('classifiers/'+filename, 'r') as f:
            data = json.loads(f.read())
        assert(data.keys() == self.allKeys)
        for k,v in data.items():
            self.classifiers[k].load(v)
    def save(self, filename):
        state = {}
        for k in self.classifiers.keys():
            state[k] = self.classifiers[k].save()
        with open('classifiers/'+filename, 'w') as f:
            f.write(json.dump(state))


class Classifier:
    class ClassifierError(Exception):
        pass
    def __init__(self,dimensions):
        self.trained = True
        self.trainData = []

    def addTrainData(self, x, result=True):
        self.trainData.append( (x, result) )
    def train(self):
        if len(self.trainData) == 0:
            raise self.ClassifierError("No training data.")
        self.trained = True

    def classify(self, x):
        if not self.trained:
            raise self.ClassifierError("Classifier not trained.")
    
    def load(self,data):
        raise NotImplementedError
    def save(self):
        raise NotImplementedError
        

class LinearRegression(Classifier):
    def __init__(self,dimensions):
        super().__init__(dimensions)
        self.regression,self.noise = [0 for _ in range(dimensions)],[0 for _ in range(dimensions)]
    
    def train(self):
        super().train()
        # training
        # ...

    def classify(self,x):
        super().classify()
        # classification
        # ...

    def load(self, data):
        try:
            self.regression,self.noise = data["regression"],data["noise"]
        except:
            raise Classifier.ClassifierError("Invalid classifier file.")
        super().train()
    def save(self):
        return {"regression": self.regression, "noise": self.noise}
    
def GaussianClassifier(Classifier):
    pass
    # ...




# called directly
if __name__ == '__main__':
    from globals import *
    raise NotCallableModuleError
