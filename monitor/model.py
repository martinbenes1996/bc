
import datetime
import numpy as np
import scipy.signal as signal
import sys
import time
import _thread

sys.path.insert(0, '../collector-py/')
import cwt

def mu(x):
    return np.mean(x)
def var(x):
    return np.var(x)

cwtCoef = 1.33846 # 1.3384615384615386
edgeOrder = 8 # 7.564102564102564
signalMu = 750 # calibrate!

def waveletTransformation(x):
    return signal.cwt(x, signal.ricker, [cwtCoef])[0]
def edges(x):
    coefs = waveletTransformation(x)
    extr = signal.argrelextrema(coefs, np.greater, order=edgeOrder)[0]
    if extr[0] != 0:
        extr = np.concatenate(([0],extr))
    if extr[-1] != len(x) - 1:
        extr = np.concatenate((extr,[len(x) - 1]))
    return extr
def segBorders(x):
    e = edges(x)
    return np.array([ (e[i-1],e[i]) for i in range(1,len(e)) ])
def segmentize(x):
    segmentBorders = segBorders(x)
    return np.array([ x[b[0]:b[1]] for b in segmentBorders])
def segLens(segs):
    return np.array([ np.size(b) for b in segs])
def segStarts(segs):
    l,starts = 0,[0]
    for s in segLens(segs):
        l += s
        starts.append(l)
    return np.array(starts)
def segMus(segs):
    return np.array([mu(seg) for seg in segs])
def segVars(segs):
    return np.array([var(seg) for seg in segs])
def segMuDeltas(segs):
    segmus = segMus(segs)
    return np.array([segmus[i+1]-segmus[i] for i in range(len(segmus)-1)])
def segVarDeltas(segs):
    segvars = segVars(segs)
    return np.array([segvars[i+1]-segvars[i] for i in range(len(segvars)-1)])


objectBorderMuCoef = 100
objectBorderVarCoef = 100
def isBorder(mu1,mu2):
    return ( abs(mu2-mu1)/objectBorderMuCoef ) > 1
def objectBorders(segs):
    segmus = segMuDeltas(segs)
    extr = [ i for i in range(1,len(segmus)) if isBorder(segmus[i-1],segmus[i]) ]
    if len(extr) > 0 and extr[0] != 0:
        extr = np.concatenate(([0],extr))
    if extr[-1] != len(segmus) - 1:
        extr = np.concatenate((extr,[len(segmus) - 1]))
    #segvars = segVarDeltas(segs)
    #extr = [ i for i in range(1,len(segvars)) if isBorder(segvars[i-1],segvars[i]) ]
    #if extr[0] != 0:
    #    extr = np.concatenate(([0],extr))
    #if extr[-1] != len(segvars) - 1:
    #    extr = np.concatenate((extr,[len(segvars) - 1]))
    return np.array([ (extr[i-1],extr[i]) for i in range(1,len(extr)) ])
def objectSegments(segs):
    return np.array([ segs[b[0]:b[1]] for b in objectBorders(segs)])








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
        self.engine = cwt.Transformer()

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
        features = []

        # segmentize
        segments = segmentize(x)
        # compute derived vectors
        seglens = segLens(segments)
        segmus = segMus(segments)

        # 1 - mu of segment mu's
        segmus_mu = mu(segmus)
        features.append( segmus_mu )
        

        # ...
        return features



