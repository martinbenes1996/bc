

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
import logging
import sklearn.linear_model as linear_model
import sklearn.externals as externals
import sys

import comm_replay
import datetime
import fuzzy
import globals
import segment
import threading
import time

class Extractor:
    """Adapter of classification methods.
    
    Attributes:
        indicate    Callback to indicate update in style of Test&Set.
        getData     Callback for getting data.
        engine      Engine to perform CWT from collector.
        buffer      Buffer to save CWT result in.
        filename    Filename of file to save recorded signal to.
    """
    # reader instances
    extractors = {}
    log = logging.getLogger(__name__)
    @classmethod
    def getExtractor(cls, name, source):
        """Returns extractor singleton instance.
        
        Arguments:
            name    Name.
        """
        # instantiate
        if name not in cls.extractors:
            cls.extractors[name] = cls(source.indicate, source.getSegment)
        # return existing
        return cls.extractors[name]

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
        self.buffer = np.array([[0,0],[0,0]])
        self.bufferLock = threading.Lock()
        self._stop = False
        self.stopLock = threading.Lock()
        # connect to collector
        self.engine = Classification.getTrained()

        # run processing thread
        threading.Thread(target=self.process).start()

    def process(self):
        """Processes data to CWT. Main for separated thread."""
        while True:
            # if changed
            if self.indicate(False):

                # feature extraction
                try:
                    features = self.extract( self.getData() )
                except Exception as e:
                    self.log.warning("data parsing error")
                    continue

                # classification
                try:
                    area = self.engine.classify( features )
                except Exception as e:
                    self.log.warning("classification error")
                    continue
                #for f in features: # for each artefact
                #    pass
                
                # update shared buffer
                with self.bufferLock:
                    self.buffer = area
                # write to file, when recording
                self.write(area)

            # wait 200 ms
            time.sleep(0.2)

            if globals.quit:
                return
            with self.stopLock:
                if self._stop:
                    return
    def stop(self):
        """Stops the model processing."""
        with self.stopLock:
            self._stop = True
    
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
                self.log.info("recording ended")
                self.filename = ''
                return
            # generate name
            name = "CWT " + str(datetime.datetime.now()) + ".dat"
        # start recording
        self.filename = name
        self.log.info("recording started")
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
        """Extracts the features.
        
        Arguments:
            x       Sample vector.
        """
        artefacts = segment.Artefact.parseArtefacts(x)
        return [a.getFeatures() for a in artefacts]


class Reference:
    """Reference holder.
    
    Static attributes:
        TRAINTEST_RATIO     Ratio of train and test.
    Attributes:
        _data               Data to parse.
        _filename           Name of the file.
    """
    TRAINTEST_RATIO = (2/3)
    def __init__(self, data, filename="<noname>"):
        """Constructor of Reference.
        
        Arguments:
            data
            filename
        """
        self._data = data
        self._filename = filename
    
    def getArtefactReference(self, artefact_index):
        """Returns the reference of artefact with given artefact index.
        
        Arguments:
            artefact_index      Index of artefact.
        """
        r = self._data[artefact_index]["key"]
        return { "presence": self.boolToFuzzy(r[0]), "center": self.boolToFuzzy(r[1]), "left": self.boolToFuzzy(r[2]), "distance": self.boolToFuzzy(r[3]) }

    def getSampleReference(self, sample_index):
        """Returns the reference of sample with given sample index.
        
        Arguments:
            sample_index        Index of sample.
        """
        artefact_index = self.artefactOfSample(sample_index)
        return self.getArtefactReference(artefact_index)
    def getRangeReference(self, range_start, range_end):
        """Returns the reference of range between two sample indices.
        Interpolates the reference value dependent on the artefact reference.
        
        Arguments:
            range_start         Index of the start sample.
            range_end           Index of the end sample.
        """
        # initiate
        range_end -= 1
        assert(range_start <= range_end)
        range_len = range_end - range_start + 1
        # parse indices into artefact indixes
        start_artefact = self.artefactOfSample(range_start)
        end_artefact = self.artefactOfSample(range_end, start_artefact)
        if start_artefact == end_artefact:
            return self.getArtefactReference(start_artefact)
        # get the interpolation coefficients
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
        # count the interpolation
        result = {"presence":0,"center":0,"left":0,"distance":0}
        N = {"presence":range_len, "center":range_len, "left":range_len, "distance":range_len}
        for k,v in r.items():
            for i,key in enumerate(("presence","center","left","distance")):
                if self._data[k]["key"][i] == True:
                    result[key] += v
                elif self._data[k]["key"][i] == None:
                    N[key] -= v
        # return
        for key in ("presence","center","left","distance"):
            if N[key] == 0:
                result[key] = None
            else:
                result[key] /= N[key]
        return result
    def getDataPath(self):
        """Returns data path."""
        return "../data/"+self._filename[:-2]+"/"+self._filename+".csv"
                    

    def artefactOfSample(self, sample_index, start_hint=0):
        """Converts sample index to artefact index.
        
        Arguments:
            sample_index    Index of the sample.
            start_hint      Hint for the start.
        """
        i = start_hint
        while True:
            if sample_index >= self._data[i]["start"] and sample_index < (self._data[i]["start"]+self._data[i]["length"]):
                return i
            else:
                i += 1
                assert(i < len(self._data))

            
    @classmethod
    def generateReferences(cls, name, traintest=False):
        """Generates the Reference instances for the session name.
        
        Arguments:
            name            Name of the session.
            traintest       Set up train-test separation.
        """
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
        """Converts 3-value to fuzzy value.
        
        Arguments:
            val             3-value logic.
        """
        if val is True:
            return 1.0
        elif val is False:
            return 0.0
        elif val is None:
            return None
        elif val >= 0 and val <= 1:
            return val

class Classification:
    """Container for classifiers and related functions.
    
    Static arguments:
        log             Logging instance.
        trainSet        Train set.
        testSet         Test set.
    Arguments:
        rows            Row count of area.
        columns         Columns count of area.
        area            Area array.
        classifiers     Classifier list.
    """
    trainSet = None
    testSet = None
    log = logging.getLogger(__name__)

    def __init__(self, featureDimension = 5):
        """Constructor of Classification class.
        
        Arguments:
            featureDimension
        """
        self.rows,self.columns = 2,3
        self.area = [[0 for _ in range(self.columns)] for _ in range(self.rows)]
        self.classifiers = {'presence' : LinearRegression(featureDimension),
                            'distance' : LinearRegression(featureDimension),
                            'center' : LinearRegression(featureDimension),
                            'left' : LinearRegression(featureDimension)}
    
    def load(self):
        """Loads the trained classifiers."""
        for k,c in self.classifiers.items():
            c.load('classifier-'+k)
        self.log.info("classifier loaded")
        return self

    def addTrainData(self, dirname):
        """Adding training data.
        
        Arguments:
            dirname     Session name.
        """
        # create references
        references,_ = Reference.generateReferences(dirname,traintest=True)
        self.log.info("reading "+dirname)
        # go through references
        for filename,trainReference in references.items():
            x = comm_replay.Reader.readFile('../data/'+dirname+'/'+filename+'.csv')
            artefacts = segment.Artefact.parseArtefacts(x)
            # iterate over artefacts
            startIt = 0
            for i,a in enumerate(artefacts):
                N = a.len()
                referenceKey = trainReference.getArtefactReference(i)
                presenceKey,centerKey,leftKey,distanceKey = referenceKey["presence"],referenceKey["center"],referenceKey["left"],referenceKey["distance"]
                features = a.getFeatures()
                self.classifiers['presence'].addTrainData(features, presenceKey)
                self.classifiers['center'].addTrainData(features, centerKey)
                self.classifiers['left'].addTrainData(features, leftKey)
                self.classifiers['distance'].addTrainData(features, distanceKey)
                startIt += N

    def train(self, save=False):
        """Trains the classifier with the pre-added data.
        
        Arguments:
            save        Makes persistent.
        """
        self.log.info("training")
        for k,c in self.classifiers.items():
            c.train()
        if save:
            self.save()

    def save(self):
        """Saves the trained classifiers."""
        status = True
        for k,c in self.classifiers.items():
            try:
                c.save('classifier-'+k)
            except Exception as e:
                status = False
        if status:
            self.log.info("classifiers saved")
    
    def test(self, testSet = None):
        """Performs the tests from the test set.
        
        Arguments:
            testSet     Test set, if None, then read from file.
        """
        if testSet == None:
            testSet = self.getTestSet()
        # perform tests
        return dict( (testItem, self.performTest(testItem)) for testItem in testSet )

    def evaluate(self, testSet=None):
        """Performs the tests from the test set.
        
        Arguments:
            testSet             Test set, if None, then read from file.
        """
        if testSet == None:
            testSet = self.getTestSet()
        # perform tests
        result,Ns = {},{}
        for testItem in testSet:
            result[testItem],Ns[testItem] = self.performTest(testItem,True)
        return result,Ns

    def classify(self, featuresVector, partial=False):
        """Classifies the score of featuresVector using trained classifier.
        
        Arguments:
            featuresVector      The input feature vector.
            partial             Returns partial result.
        """
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

        score = {'presence': np.mean(presence), 'distance': np.mean(distance), 'center': np.mean(center), 'left': np.mean(left)}
        if partial:
            score=[]
            for i,_ in enumerate(presence):
                score.append( {'presence':presence[i],'distance':distance[i],'left':left[i],'center':center[i]} )
            return score
        
        AND = fuzzy.SNorm.method('product')
        areaM[0][0] = AND(score['presence'], score['distance'] )
        areaM[0][1] = AND(score['presence'], score['distance'] )
        areaM[1][0] = AND(score['presence'], N(score['distance']) )
        areaM[1][1] = AND(score['presence'], N(score['distance']) )
        return areaM

    @classmethod
    def retrain(cls, trainSet=None):
        """Trains the classifiers.
        
        Arguments:
            trainSet        Training set. If None, then from file.
        """
        if trainSet == None:
            trainSet = cls.getTrainSet()
        c = cls()
        for t in trainSet:
            c.addTrainData(t)
        c.train(save=True)
        return c

    @classmethod
    def getTrained(cls):
        """Returns trained classifier (either trains, or get trained)."""
        c = cls()
        try:
            return c.load()
        except:
            return cls.retrain()
    
    @classmethod
    def getTrainSet(cls):
        """Returns training set."""
        if cls.trainSet == None:
            cls.trainSet = cls.readTrainSet()
        return cls.trainSet
    @classmethod
    def getTestSet(cls):
        """Returns testing set."""
        if cls.testSet == None:
            cls.testSet = cls.readTestSet()
        return cls.testSet
    @staticmethod
    def readTrainSet():
        """Reads training set from file."""
        with open('classifiers/trainset.json','r') as ts:
            return json.load(ts)
    @staticmethod
    def readTestSet():
        """Reads testing set from file."""
        with open('classifiers/testset.json','r') as ts:
            return json.load(ts)

    @classmethod
    def setTrainSet(cls, trainSet, persistent=False):
        """Sets training set to the container.
        
        Arguments:
            trainSet        Training set names.
            persistent      Set the set to the file.
        """
        cls.trainSet = trainSet
        if persistent:
            with open('classifiers/trainset.json','w') as ts:
                json.dump(trainSet,ts)
    @classmethod
    def setTestSet(cls, testSet, persistent=False):
        """Sets testing set to the container.
        
        Arguments:
            testSet         Testing set names.
            persistent      Set the set to the file.
        """
        cls.testSet = testSet
        if persistent:
            with open('classifiers/testset.json','w') as ts:
                json.dump(testSet,ts)
    
    def performTest(self, dirname, segmentsizes=False):
        """Performs the test with a name.
        
        Arguments:
            dirname         Directory name.
            segmentsizes    Sizes of segments.
        """
        _,tests = Reference.generateReferences(dirname, True)
        self.log.info("reading "+dirname)
        results = []
        testNs = []
        for testName,testReference in tests.items():
            x = comm_replay.Reader.readFile(testReference.getDataPath())
            artefacts = segment.Artefact.parseArtefacts(x)
            featureSet = [ a.getFeatures() for a in artefacts]

            scoreSet = self.classify(featureSet, partial=True)
            
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
    """Interface for classifier classes.
    
    Attributes:
        sigmoid         Sigmoid for the classifier output.
        trainData       Data to train.
        trained         Indicator if classifier is trained.
    """

    class ClassifierError(Exception):
        """Exception for Classifier."""
        pass

    def __init__(self, sigmoid):
        """Constructor of Classifier.
        
        Arguments:
            sigmoid     Sigmoid for the classifier output.
        """
        self.trained = True
        self.trainData = []
        self.sigmoid = sigmoid

    def addTrainData(self, x, result=True):
        """Adds the training data.
        
        Arguments:
            x           Training data.
            result      Reference value.
        """
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
        """Trains the classifier.
        
        Arguments:
            loaded      
        """
        if not loaded and len(self.trainData) == 0:
            raise self.ClassifierError("No training data.")
        self.trained = True

    def classify(self, x):
        """Classifies and returns the score.
        
        Arguments:
            x           Input.
        """
        if not self.trained:
            raise self.ClassifierError("Classifier not trained.")
    
    def load(self, filename):
        """Loads the classifier state.
        
        Arguments:
            filename    Name of the file.
        """
        raise NotImplementedError
    def save(self):
        """Saves the classifier state."""
        raise NotImplementedError
    
    @staticmethod
    def logistic(x):
        """Logistic sigmoid.
        
        Arguments:
            x           Input.
        """
        return 1 / (1 + math.exp(-x))
    @staticmethod
    def arctan(x):
        """Arctangens.
        
        Arguments:
            x           Input.
        """
        return math.atan(x)
    @staticmethod
    def mySigmoid(x):
        """My sigmoid.
        
        Arguments:
            x           Input.
        """
        return 1 / math.sqrt(1 + x**2)
        

class LinearRegression(Classifier):
    """Linear regression implementing interface for classifier classes.
    
    Static attributes:
        smoothenSlopePresenceForwards       Coefficient for forward smoothening of slope for presence.
        smoothenSlopePresenceBackwards      Coefficient for backward smoothening of slope for presence.
        smoothenSlopeDistanceForwards       Coefficient for forward smoothening of slope for distance.
        smoothenSlopeDistanceBackwards      Coefficient for backward smoothening of slope for distance.
        smoothenSlopeCenterForwards         Coefficient for forward smoothening of slope for center.
        smoothenSlopeCenterBackwards        Coefficient for backward smoothening of slope for center.

    Attributes:
        clf             Classifier instance.
    """

    def __init__(self, sigmoid=Classifier.logistic):
        """Linear regression constructor.
        
        Arguments:
            sigmoid     Used sigmoid.
        """
        super().__init__(sigmoid=sigmoid)
        self.clf = linear_model.SGDClassifier(max_iter=1000, tol=1e-3)

    def train(self):
        """Trains the classifier with added data."""
        super().train()
        X = np.array([d[0] for d in self.trainData])
        Y = np.array([d[1] for d in self.trainData])
        # training
        try:
            self.clf.fit(X,Y)
        except ValueError:
            for i in X:
                pass
            raise

    def classify(self, x):
        """Classifies and returns the score for input.
        
        Arguments:
            x       Input.
        """
        super().classify(x)
        # classification
        return self.clf.decision_function( np.array([x]) )[0]

    def load(self, filename):
        """Loads the classifier state.
        
        Arguments:
            filename    Filename of the state file.
        """
        try:
            self.clf = externals.joblib.load('classifiers/'+filename+'.sav')
        except:
            raise Classifier.ClassifierError("Invalid classifier file.")
        super().train(loaded=True)
        
    def save(self, filename):
        """Saves the state into filename.
        
        Arguments:
            filename    Filename to save to.
        """
        externals.joblib.dump(self.clf, 'classifiers/'+filename+'.sav')
    
    smoothenSlopePresenceForwards = -0.05
    smoothenSlopePresenceBackwards = -0.001
    @classmethod
    def postprocessPresence(cls, presence, Ns):
        """Processes the presence.
        
        Arguments:
            presence    Presence scores.
            Ns          Sizes of artefacts.
        """
        return cls.smoothenBothSides(presence, Ns, cls.smoothenSlopePresenceForwards, cls.smoothenSlopePresenceBackwards)
    
    smoothenSlopeDistanceForwards = -0.001
    smoothenSlopeDistanceBackwards = -0.1
    @classmethod
    def postprocessDistance(cls, distance, presence, Ns):
        """Processes the distance.
        
        Arguments:
            distance    Distance scores.
            presence    Presence scores.
            Ns          Sizes of artefacts.
        """
        # process
        grounded = np.absolute( np.array(distance) - np.mean(distance) )
        smoothened = cls.smoothenBothSides(grounded, Ns, cls.smoothenSlopeDistanceForwards, cls.smoothenSlopeDistanceBackwards)
        return np.minimum(np.array(smoothened), np.array(presence))
    
    smoothenSlopeCenterForwards = -0.005
    smoothenSlopeCenterBackwards = -0.015
    @classmethod
    def postprocessCenter(cls, center, presence, Ns):
        """Processes the center.
        
        Arguments:
            center      Center scores.
            presence    Presence scores.
            Ns          Sizes of artefacts.
        """
        # process
        grounded = center
        smoothened = cls.smoothenBothSides(grounded, Ns, cls.smoothenSlopeCenterForwards, cls.smoothenSlopeCenterBackwards)
        return np.minimum(np.array(smoothened), np.array(presence))
    
    @classmethod
    def smoothenBothSides(cls, x, Ns, kF, kB):
        """Smoothes signal from both sides.
        
        Arguments:
            x           Input signal.
            Ns          Artefact sizes.
            kF          Forward smoothening coefficients.
            kB          Backward smoothening coefficients.
        """
        forward = cls.smoothen(x, Ns, kF)
        backward = np.flip(cls.smoothen(np.flip(x,0), Ns, kB), 0)
        return [fuzzy.TConorm.maximum(forward[i],backward[i]) for i in range(len(forward))]

    @staticmethod
    def smoothen(x, Ns, k=-1):
        """Smoothes signal.
        
        Arguments:
            x           Input signal.
            Ns          Artefact sizes.
            k           Smoothening coefficient.
        """
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
    """Gaussian classifier implementing the classifier interface."""

    def __init__(self, sigmoid=Classifier.logistic):
        """Constructs the Gaussian classifier.
        
        Arguments:
            sigmoid     Sigmoid to precess the output with.
        """
        super().__init__(sigmoid=sigmoid)
    pass
    # ...




# called directly
if __name__ == '__main__':
    from globals import *
    raise NotCallableModuleError
