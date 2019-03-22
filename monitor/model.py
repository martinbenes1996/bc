
import datetime
import numpy as np
import scipy.signal as signal
import sys
import time
import _thread

import fuzzy

sys.path.insert(0, '../collector-py/')
import cwt


def scoreSS_(edge):
    return 1 - Khi["S"](edge[0])*Khi["S"](edge[1])
def scoreFF_(edge):
    return 1 - Khi["F"](edge[0])*Khi["F"](edge[1])
def scoreRR_(edge):
    return 1 - Khi["R"](edge[0])*Khi["R"](edge[1])
def scoreRSR(edge):
    return 
def scoreBorder(segs, i):
    edges = segment.Edge.edgify(segs)
    scores = {}
    # SS*
    scores["SSS"] = scoreSS_(edges)
    scores["SSF"] = scoreSS_(edges)
    scores["SSR"] = scoreSS_(edges)
    # FF*
    scores["FFS"] = scoreFF_(edges)
    scores["FFF"] = scoreFF_(edges)
    scores["FFR"] = scoreFF_(edges)
    # RR*
    scores["RRS"] = scoreRR_(edges)
    scores["RRF"] = scoreRR_(edges)
    scores["RRR"] = scoreRR_(edges)
    # RSR
    scores["RSR"] = scoreRSR(edges)



def isBorder(segs, i):
    def stagnates(segs):
        return (abs(mu(segs[1])-mu(segs[0]))/toleranceMu) < 1
    def rises(segs):
        return not stagnates(segs) and (mu(segs[1])-mu(segs[0])) > 0
    def falls(segs):
        return not stagnates(segs) and (mu(segs[1])-mu(segs[0])) < 0
    def hasSameCharacter(segs):
        return (var(segs[1])-var(segs[0])) / toleranceVar < 1
    def wilds(segs):
        return not hasSameCharacter(segs) and (var(segs[1])-var(segs[0])) > 0
    def calms(segs):
        return not hasSameCharacter(segs) and (var(segs[1])-var(segs[0])) < 0
    def describe(e):
        if stagnates(e):
            return "S"
        elif rises(e):
            return "R"
        elif falls(e):
            return "F"
        else:
            return "_"
    def getDescriptor(edges):
        return describe(edges[0]) + describe(edges[1]) + describe(edges[2])

    previousEdge = segs[0:2]
    currentEdge = segs[1:3]
    nextEdge = segs[2:4]

    descr = getDescriptor( (previousEdge,currentEdge, nextEdge) )
    print(i, ":", descr)

    val = 0
    if descr in {"SSS", "FFF", "RRR"}:
        val = 0
    # left changes
    elif descr in {"RFF", "FRR", "SFF", "SRR", "FSS", "RSS"}:
        val = 1
    # right changes
    elif descr in {"SSR", "SSF", "RRF", "RRS", "FFR", "FFS"}:
        val = 0
    # center changes
    elif descr in {"SFS", "RFR", "SRS", "FRF", "RSR", "FSF"}:
        val = 1
    # both changes
    elif descr in {"SRF", "FRS", "FSR", "RSF", "RFS", "SFR"}:
        val = 0
    # unhandled
    else:
        print("Unhandled: ", descr)
        val = 1

    return val > 0.5

def getEdges(segs):
    segmus = segMuDeltas(segs)
    return np.array([0] + [i for i in range(2,len(segmus)-1) if isBorder(segs[i-2:i+2], i)] + [len(segmus)-1])
def objectBorders(segs):
    extr = getEdges(segs)
    return np.array([ (extr[i-1],extr[i]) for i in range(1,len(extr)) ])
def objectSegments(segs):
    return np.array([ segs[int(b[0]):int(b[1])] for b in objectBorders(segs) ])








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



