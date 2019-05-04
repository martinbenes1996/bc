

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
import globals
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

class Reference:
    TRAINTEST_RATIO = (2/3)
    def __init__(self, data, filename="<noname>"):
        self._data = data
        self._filename = filename
    
    def getArtefactReference(self, artefact_index):
        r = self._data[artefact_index]["key"]
        return { "presence": self.boolToFuzzy(r[0]), "center": self.boolToFuzzy(r[1]), "left": self.boolToFuzzy(r[2]), "distance": self.boolToFuzzy(r[3]) }

    def getSampleReference(self, sample_index):
        artefact_index = self.artefactOfSample(sample_index)
        return self.getArtefactReference(artefact_index)
    def getRangeReference(self, range_start, range_end):
        range_end -= 1
        assert(range_start <= range_end)
        range_len = range_end - range_start + 1
        start_artefact = self.artefactOfSample(range_start)
        end_artefact = self.artefactOfSample(range_end, start_artefact)
        if start_artefact == end_artefact:
            #print("Same artefact:", range_start, start_artefact, range_end, end_artefact)
            return self.getArtefactReference(start_artefact)
        r = {}
        for artefactindex in range(start_artefact, end_artefact+1):
            artefact = self._data[artefactindex]
            a_start,a_len = artefact["start"],artefact["length"]
            a_end = a_start + a_len
            if a_start < range_start:
                r[artefactindex] = a_end - range_start
            elif a_end > range_end:
                r[artefactindex] = range_end - a_start + 1
            else:
                r[artefactindex] = a_len
        assert(sum(list(r.values())) == range_len)
        result = {"presence":0,"center":0,"left":0,"distance":0}
        N = {"presence":range_len, "center":range_len, "left":range_len, "distance":range_len}
        for k,v in r.items():
            for i,key in enumerate(("presence","center","left","distance")):
                if self._data[k]["key"][i] == True:
                    result[key] += v
                elif self._data[k]["key"][i] == None:
                    N[key] -= v
        for key in ("presence","center","left","distance"):
            if N[key] == 0:
                result[key] = None
            else:
                result[key] /= N[key]
        return result
    def getDataPath(self):
        return "../data/"+self._filename[:-2]+"/"+self._filename+".csv"
                    

    def artefactOfSample(self, sample_index, start_hint=0):
        i = start_hint
        while True:
            if sample_index >= self._data[i]["start"] and sample_index < (self._data[i]["start"]+self._data[i]["length"]):
                return i
            else:
                i += 1
                assert(i < len(self._data))

            
    @classmethod
    def generateReferences(cls, name, traintest=False):
        with open('../data/'+name+'/label.json') as f:
            data = json.load(f)
            files = sorted(list(data.keys()))
            result = dict( (filename,cls(data[filename], filename)) for filename in files )
            if not traintest:
                return result
            else:
                assert(cls.TRAINTEST_RATIO >= 0 and cls.TRAINTEST_RATIO <= 1)
                traincnt = int(len(files) * cls.TRAINTEST_RATIO)
                trains = dict( (filename,result[filename]) for filename in files[:traincnt])
                tests = dict( (filename,result[filename]) for filename in files[traincnt:])
                return trains,tests
    @staticmethod
    def boolToFuzzy(val):
        if val is True:
            return 1.0
        elif val is False:
            return 0.0
        elif val is None:
            return None
        elif val >= 0 and val <= 1:
            return val

class Classification:
    trainSet = None
    testSet = None
    def __init__(self, featureDimension = 5):
        self.rows,self.columns = 2,3
        self.area = [[0 for _ in range(self.columns)] for _ in range(self.rows)]
        self.classifiers = {'presence' : LinearRegression(featureDimension),
                            'distance' : LinearRegression(featureDimension),
                            'center' : LinearRegression(featureDimension),
                            'left' : LinearRegression(featureDimension)}
    
    def load(self):
        for k,c in self.classifiers.items():
            c.load('classifier-'+k)
        print("Classifier loaded.")
        return self

    def addTrainData(self, dirname):
        references,_ = Reference.generateReferences(dirname,traintest=True)
        print("Training with", dirname+'...')
        for filename,trainReference in references.items():
            x = comm_replay.Reader.readFile('../data/'+dirname+'/'+filename+'.csv')
            artefacts = segment.Artefact.parseArtefacts(x)

            startIt = 0
            for i,a in enumerate(artefacts):
                N = a.len()
                referenceKey = trainReference.getArtefactReference(i)#startIt,startIt+N)
                presenceKey,centerKey,leftKey,distanceKey = referenceKey["presence"],referenceKey["center"],referenceKey["left"],referenceKey["distance"]
                features = a.getFeatures()
                self.classifiers['presence'].addTrainData(features, presenceKey)
                self.classifiers['center'].addTrainData(features, centerKey)
                self.classifiers['left'].addTrainData(features, leftKey)
                self.classifiers['distance'].addTrainData(features, distanceKey)
                startIt += N


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
    
    def test(self, testSet = None):
        if testSet == None:
            testSet = self.getTestSet()
        # perform tests
        return dict( (testItem, self.performTest(testItem)) for testItem in testSet )
    def evaluate(self,testSet=None):
        if testSet == None:
            testSet = self.getTestSet()
        # perform tests
        result,Ns = {},{}
        for testItem in testSet:
            result[testItem],Ns[testItem] = self.performTest(testItem,True)
        return result,Ns

    def classify(self, featuresVector):
        areaM = [[0 for _ in range(2)] for _ in range(2)] # 2x2 matrix
        rawPresence,rawDistance,rawLeft,rawCenter = [],[],[],[]
        artefactsLengths = [segment.Artefact.artefactLength(x) for x in featuresVector]
        for x in featuresVector:
            rawPresence.append(self.classifiers['presence'].classify(x))
            rawDistance.append(self.classifiers['distance'].classify(x))
            rawLeft.append(self.classifiers['left'].classify(x))
            rawCenter.append(self.classifiers['center'].classify(x))
        
        
        # fuzzification
        presence = globals.normalize(rawPresence)
        distance = globals.normalize(rawDistance)
        left = globals.normalize(rawLeft)
        center = globals.normalize(rawCenter)

        # postprocessing
        N = fuzzy.Negator.method('standard')
        presence = self.classifiers['presence'].postprocessPresence(presence, artefactsLengths)
        center = self.classifiers['center'].postprocessCenter(center, presence, artefactsLengths)
        left = N(left)
        distance = self.classifiers['distance'].postprocessDistance(distance, presence, artefactsLengths)

        # delete
        score = []
        for i,_ in enumerate(presence):
            score.append( {'presence':presence[i],'distance':distance[i],'left':left[i],'center':center[i]} )
        return score
        
        AND = fuzzy.SNorm.method('product')
        areaM[0][0] = AND(score['presence'],   score['distance'],    score['left'])
        areaM[0][1] = AND(score['presence'],   score['distance'],  N(score['left']))
        areaM[1][0] = AND(score['presence'], N(score['distance']),   score['left'])
        areaM[1][1] = AND(score['presence'], N(score['distance']), N(score['left']))
        return areaM


    @classmethod
    def retrain(cls, trainSet=None):
        if trainSet == None:
            trainSet = cls.getTrainSet()
        c = cls()
        for t in trainSet:
            c.addTrainData(t)
        c.train(save=True)
        return c

    @classmethod
    def getTrained(cls):
        c = cls()
        try:
            return c.load()
        except:
            return cls.retrain()
    
    @classmethod
    def getTrainSet(cls):
        if cls.trainSet == None:
            cls.trainSet = cls.readTrainSet()
        return cls.trainSet
    @classmethod
    def getTestSet(cls):
        if cls.testSet == None:
            cls.testSet = cls.readTestSet()
        return cls.testSet
    @staticmethod
    def readTrainSet():
        with open('classifiers/trainset.json','r') as ts:
            return json.load(ts)
    @staticmethod
    def readTestSet():
        with open('classifiers/testset.json','r') as ts:
            return json.load(ts)

    @classmethod
    def setTrainSet(cls, trainSet, persistent=False):
        cls.trainSet = trainSet
        if persistent:
            with open('classifiers/trainset.json','w') as ts:
                json.dump(trainSet,ts)
    @classmethod
    def setTestSet(cls, testSet, persistent=False):
        cls.testSet = testSet
        if persistent:
            with open('classifiers/testset.json','w') as ts:
                json.dump(testSet,ts)
    
    def performTest(self, dirname, segmentsizes=False):
        _,tests = Reference.generateReferences(dirname, True)
        print("Testing with", dirname+'...')
        results = []
        testNs = []
        for testName,testReference in tests.items():
            x = comm_replay.Reader.readFile(testReference.getDataPath())
            artefacts = segment.Artefact.parseArtefacts(x)

            featureSet = [ a.getFeatures() for a in artefacts]

            scoreSet = self.classify(featureSet)
            
            startIt = 0
            artefactNs = []
            for i,a in enumerate(artefacts):
                N = a.len()
                artefactNs.append(N)
                referenceKey = testReference.getRangeReference(startIt,startIt+N)
                presenceKey,centerKey,leftKey,distanceKey = referenceKey["presence"],referenceKey["center"],referenceKey["left"],referenceKey["distance"]

                presenceScore = scoreSet[i]['presence']
                centerScore = scoreSet[i]['center']
                leftScore = scoreSet[i]['left']
                distanceScore = scoreSet[i]['distance']
                results.append({'presence':(presenceScore,presenceKey),
                                'center':(centerScore,centerKey),
                                'left':(leftScore,leftKey),
                                'distance':(distanceScore,distanceKey)})
                startIt += N
            testNs.append(artefactNs)
        if not segmentsizes:
            return results
        else:
            return results,testNs


class Classifier:
    class ClassifierError(Exception):
        pass
    def __init__(self, sigmoid):
        self.trained = True
        self.trainData = []
        self.sigmoid = sigmoid

    def addTrainData(self, x, result=True):
        if result is True:
            assignClass = 2
        elif result is False:
            assignClass = 1
        elif result is None:
            return
        elif result >= 0.5:
            assignClass = 2
        elif result < 0.5:
            assignClass = 1
        if x is None:
            raise ValueError
        self.trainData.append( (x, assignClass) )
    def train(self, loaded=False):
        if not loaded and len(self.trainData) == 0:
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
        #self.clf = linear_model.LogisticRegression(max_iter=1000, tol=1e-3)

    
    def train(self):
        super().train()
        X = np.array([d[0] for d in self.trainData])
        Y = np.array([d[1] for d in self.trainData])
        # training
        try:
            self.clf.fit(X,Y)
        except ValueError:
            for i in X:
                print(i)
            raise

    def classify(self,x):
        super().classify(x)
        # classification
        return self.clf.decision_function( np.array([x]) )[0]

    def load(self, filename):
        try:
            self.clf = externals.joblib.load('classifiers/'+filename+'.sav')
        except:
            raise Classifier.ClassifierError("Invalid classifier file.")
        super().train(loaded=True)
        
    def save(self, filename):
        externals.joblib.dump(self.clf, 'classifiers/'+filename+'.sav')
    
    smoothenSlopePresenceForwards = -0.085
    smoothenSlopePresenceBackwards = -0.001#-0.0025
    @classmethod
    def postprocessPresence(cls, presence, Ns):
        # smooth from forwards and backwards
        #forward = cls.smoothen(presence, Ns,cls.smoothenSlopePresenceForwards )
        #backward = np.flip( cls.smoothen( np.flip(presence,0), Ns,cls.smoothenSlopePresenceBackwards ),0 )
        #return [fuzzy.TConorm.maximum(forward[i],backward[i]) for i in range(len(forward))]
        #presence = np.absolute( np.array(presence) - np.mean(presence) )
        return cls.smoothenBothSides(presence, Ns, cls.smoothenSlopePresenceForwards, cls.smoothenSlopePresenceBackwards)
    
    smoothenSlopeDistanceForwards = -0.001
    smoothenSlopeDistanceBackwards = -0.1
    @classmethod
    def postprocessDistance(cls, distance, presence, Ns):
        # process
        grounded = np.absolute( np.array(distance) - np.mean(distance) )
        #grounded = distance
        smoothened = cls.smoothenBothSides(grounded, Ns, cls.smoothenSlopeDistanceForwards, cls.smoothenSlopeDistanceBackwards)
        return np.minimum(np.array(smoothened), np.array(presence))
    
    @classmethod
    def postprocessCenter(cls, center, presence, Ns):
        # process
        return np.array(center)*np.array(presence)
    
    @classmethod
    def smoothenBothSides(cls, x, Ns, kF, kB):
        forward = cls.smoothen(x, Ns, kF)
        backward = np.flip(cls.smoothen(np.flip(x,0), Ns, kB), 0)
        return [fuzzy.TConorm.maximum(forward[i],backward[i]) for i in range(len(forward))]
    @staticmethod
    def smoothen(x, Ns, k=-1):
        assert(len(x) > 0)
        assert(len(x) == len(Ns))
        m = x[0]
        for i,p in enumerate(x):
            r = p + m
            if r > 1:
                r = 1
            x[i] = r
            m = r + Ns[i]*k
            if m < 0:
                m = 0
            if m > 1:
                m = 1
        return x

def GaussianClassifier(Classifier):
    def __init__(self, sigmoid=Classifier.logistic):
        super().__init__(sigmoid=sigmoid)
    pass
    # ...




# called directly
if __name__ == '__main__':
    from globals import *
    raise NotCallableModuleError
