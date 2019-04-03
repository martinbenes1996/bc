

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
import sklearn.linear_model as linear_model
import sklearn.externals as externals
import sys

import comm_replay
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
    def __init__(self, featureDimension = 5):
        self.rows,self.columns = 2,3
        self.area = [[0 for _ in range(self.columns)] for _ in range(self.rows)]
        self.classifiers = {'presence' : LinearRegression(featureDimension),
                            'distance' : LinearRegression(featureDimension),
                            'center' : LinearRegression(featureDimension),
                            'left' : LinearRegression(featureDimension)}
    
    def load(self):
        pass

    def addTrainData(self, dirname):
        with open('../data/'+dirname+'/train.json', 'r') as f:
            labels = json.loads(f.read())
        print("Training with", dirname+'...')
        for labelfilename,labeldata in labels.items():
            x = comm_replay.Reader.readFile('../data/'+dirname+'/'+labelfilename+'.csv')
            artefacts = segment.Artefact.parseArtefacts(x)
            assert(len(artefacts) == len(labeldata))
            for i,a in enumerate(artefacts):
                presenceKey,centerKey,leftKey,distanceKey = labeldata[i]['key']
                features = a.getFeatures()
                #print('Train: presence', presenceKey, 'center', centerKey, 'left', leftKey, 'distance', distanceKey)
                self.classifiers['presence'].addTrainData(features, presenceKey)
                self.classifiers['center'].addTrainData(features, centerKey)
                self.classifiers['left'].addTrainData(features, leftKey)
                self.classifiers['distance'].addTrainData(features, distanceKey)
    
    def test(self, dirname):
        with open('../data/'+dirname+'/test.json', 'r') as f:
            labels = json.loads(f.read())
        print("Testing with", dirname+'...')
        for labelfilename,labeldata in labels.items():
            x = comm_replay.Reader.readFile('../data/'+dirname+'/'+labelfilename+'.csv')
            artefacts = segment.Artefact.parseArtefacts(x)
            assert(len(artefacts) == len(labeldata))
            for i,a in enumerate(artefacts):
                presenceKey,centerKey,leftKey,distanceKey = labeldata[i]['key']
                features = a.getFeatures()
                presenceScore = self.classifiers['presence'].classify(features)
                centerScore = self.classifiers['center'].classify(features)
                leftScore = self.classifiers['left'].classify(features)
                distanceScore = self.classifiers['distance'].classify(features)

                print(presenceScore, presenceKey)
                print(centerScore, centerKey)
                print(leftScore, leftKey)
                print(distanceScore, distanceKey)
                input('')


    
    def train(self, save=False):
        for k,c in self.classifiers.items():
            c.train()
        print("Classifiers trained.")
        if save:
            self.save()
        



    def save(self):
        status = True
        for k,c in self.classifiers.items():
            try:
                c.save('classifier-'+k)
            except Exception as e:
                print(e, file=sys.stderr)
                status = False
        if status:
            print("Classifiers saved.")


class Classifier:
    class ClassifierError(Exception):
        pass
    def __init__(self, sigmoid):
        self.trained = True
        self.trainData = []
        self.sigmoid = sigmoid

    def addTrainData(self, x, result=True):
        if result:
            assignClass = 2
        else:
            assignClass = 1
        self.trainData.append( (x, assignClass) )
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
    
    @staticmethod
    def logistic(x):
        return 1 / (1 + math.exp(-x))
    @staticmethod
    def arctan(x):
        return math.atan(x)
    @staticmethod
    def mySigmoid(x):
        return 1 / math.sqrt(1 + x**2)
        

class LinearRegression(Classifier):
    def __init__(self, sigmoid=Classifier.logistic):
        super().__init__(sigmoid=sigmoid)
        self.clf = linear_model.SGDClassifier(max_iter=1000, tol=1e-3)

    
    def train(self):
        super().train()
        X = np.array([d[0] for d in self.trainData])
        Y = np.array([d[1] for d in self.trainData])
        # training
        self.clf.fit(X,Y)

    def classify(self,x):
        super().classify(x)
        # classification
        return self.clf.decision_function( np.array([x]) )[0]

    def load(self, filename):
        try:
            self.clf = externals.joblib.load('classifiers/'+filename+'.sav')
        except:
            raise Classifier.ClassifierError("Invalid classifier file.")
        super().train()
        
    def save(self, filename):
        externals.joblib.dump(self.clf, 'classifiers/'+filename+'.sav')
    
def GaussianClassifier(Classifier):
    def __init__(self, sigmoid=Classifier.logistic):
        super().__init__(sigmoid=sigmoid)
    pass
    # ...




# called directly
if __name__ == '__main__':
    from globals import *
    raise NotCallableModuleError
