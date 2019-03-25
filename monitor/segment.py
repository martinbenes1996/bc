
import numpy as np
import scipy.signal as signal

import fuzzy


class Segment:
    cwtCoef = 1.33846 # 1.3384615384615386
    edgeOrder = 8 # 7.564102564102564
    signalMu = 750 # calibrate!
    
    def __init__(self, samples, position):
        self.samples = samples
        self.pos = position
    def __len__(self):
        return len(self.samples)
    def mu(self):
        return np.mean(self.samples)
    def var(self):
        return np.var(self.samples)
    def len(self):
        return len(self)
    def position(self):
        return self.pos
    def xcenter(self):
        return int(self.pos + len(self)/2)

    @classmethod
    def segmentize(cls, x):
        # changes using CWT
        coefs = signal.cwt(x, signal.ricker, [cls.cwtCoef])[0]
        extrems = signal.argrelextrema(coefs, np.greater, order=cls.edgeOrder)[0]
        if extrems[0] != 0:
            extrems = np.concatenate(([0],extrems))
        if extrems[-1] != len(x) - 1:
            extrems = np.concatenate((extrems,[len(x) - 1]))
        # segment borders
        segmentBorders = np.array([ (extrems[i-1],extrems[i]) for i in range(1,len(extrems)) ])
        # segments
        segments = np.array([ x[b[0]:b[1]] for b in segmentBorders])
        segmentList = []
        lensum = 0
        for segment in segments:
            segmentInstance = cls(segment, lensum)
            segmentList.append(segmentInstance)
            lensum += segmentInstance.len()
        return segmentList

class Edge:
    toleranceStagnation = 20
    toleranceCharacter = 2
    Khi = { "F": fuzzy.ArctangenoidSet(toleranceStagnation, 0, "L").get,
            "S": fuzzy.GaussianSet(toleranceStagnation).get,
            "R": fuzzy.ArctangenoidSet(toleranceStagnation, 0, "R").get }

    def __init__(self, segments):
        self.first, self.second = segments[0], segments[1]
    def Dmu(self):
        return self.second.mu() - self.first.mu()
    def Dvar(self):
        return self.second.var() - self.first.var()

    def muScore(self):
        return self.Dmu() #/ self.toleranceStagnation
    def varScore(self):
        return self.Dvar() #/ self.toleranceCharacter

    def stagnates(self):
        return abs(self.muScore()) <= 1
    def rises(self):
        return not self.stagnates() and self.Dmu() > 0
    def falls(self):
        return not self.stagnates() and self.Dmu() < 0

    def S(self):
        return self.Khi["S"](self.muScore())
    def R(self):
        return self.Khi["R"](self.muScore())
    def F(self):
        return self.Khi["F"](self.muScore())
    def getKhi(self, key):
        assert(key in {"S","R","F"})
        return self.Khi[key](self.muScore())
    
    def stays(self):
        return abs(self.varScore()) <= 1
    def wilds(self):
        return self.varScore() > 1
    def calms(self):
        return self.varScore() < -1
    


    @classmethod
    def edgify(cls, segments):
        return [ cls(segments[0:2]), cls(segments[1:3]), cls(segments[2:4]) ]



class Artefact:
    def __init__(self, samples, score):
        self.samples = samples
        self.score = score
        pass
    
    @classmethod
    def parseArtefacts(cls, segments):
        edges = [ Edge(segments[i:i+2]) for i in range(len(segments) - 1) ]
        edgeCombinations = [ a+b+c for a in "FSR" for b in "FSR" for c in "FSR"]

        # fill artefact fuzzy matrix
        artefactMatrix = []
        for i in range(1,len(edges)-1):

            triade = dict()
            for key in edgeCombinations:
                fuzzyCoeff = edges[i-1].getKhi(key[0])*edges[i].getKhi(key[1])*edges[i+1].getKhi(key[2])
                #if key == "SSS":
                #    print(fuzzyCoeff, "=", edges[i-1].getKhi(key[0]), edges[i].getKhi(key[1]), edges[i+1].getKhi(key[2]))
                triade[key] = cls.score(edges[i-1:i+2], key) * fuzzyCoeff
            artefactMatrix.append(triade)

        return artefactMatrix

        #artefactBorders = [ i for i in range(1,len(edges)-1) if cls.isBorder(edges[i-1:i+2])]


    @classmethod
    def score(cls, edges, key):
        prevEdge,currEdge,nextEdge = edges
        prevKhi,currKhi,nextKhi = prevEdge.getKhi(key[0]),currEdge.getKhi(key[1]),nextEdge.getKhi(key[2])
        nAlpha,nBeta,nGamma,nDelta = prevEdge.first.len(),prevEdge.second.len(),nextEdge.first.len(),nextEdge.second.len()
        n = nAlpha+nBeta+nGamma+nDelta
        # SS*, FF*, RR*
        if key[0:2] in {"SS", "FF", "RR"}:
            #return (nAlpha + nBeta) / n
            return 1
        # RSR, FSF
        elif key in {"RSR", "FSF", "SRS", "SFS"}:
            #return (nBeta + nGamma) / n
            return 1
            # or using variances
        # SFF, SRR, RSS, FSS
        elif key in {"SFF", "SRR", "RSS", "FSS"}:
            #return (nAlpha + nBeta) / n
            return 1
        # FSR, RSF
        elif key in {"FSR", "RSF"}:
            #return (nAlpha + nDelta) / n
            return 1
        # RF*, FR *
        elif key[0:2] in {"RF","FR"}:
            return 1
        # SFR, SRF
        elif key in {"SFR", "SRF"}:
            return 1
        # ???
        else:
            #return 1
            raise Exception("Bad key: " + key)





