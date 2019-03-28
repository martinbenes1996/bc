
import math
import numpy as np
import scipy.signal as signal
import sys

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
        self.fuzzyScore = dict()
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
    def __init__(self):
        self.segments = []
    def append(self, segment):
        self.segments.append(segment)

    def samples(self):
        artefactSamples = []
        for segment in self.segments:
            for sample in segment.samples:
                artefactSamples.append(sample)
        return np.array(artefactSamples)
    def mu(self):
        return np.mean(self.samples())
    def var(self):
        return np.var(self.samples())
    def len(self):
        return len(self.samples())
    
    def getFeatures(self):
        features = []
        # get description
        samples = self.samples()
        smin, smax = min(samples), max(samples)
        N = len(samples)

        # best fitting line (k)
        mu,var = self.mu(),self.var()
        minP,maxP = smin,smax
        bestScore,optimalK,optimalLine = None, None, lambda x:None
        for startP in np.linspace(minP,maxP,15):
            for endP in np.linspace(minP,maxP,15):
                # count line similarity score
                k = (endP-startP)/N
                line = [startP + k*x for x in range(N)]
                score = 0
                for i in range(N):
                    score += (samples[i]-line[i])**2
                score /= N
                if bestScore is None:
                    bestScore = score
                if abs(score) < abs(bestScore):
                    bestScore,optimalK,optimalLine = score,k,line

        #return optimalLine,optimalK

        # line slope
        features.append(optimalK)
        # difference from line
        features.append(bestScore)
        # variance of artefact
        features.append(var)
        # length of segment
        features.append(N)
        # mean value of segment
        features.append(mu)
        # ...
        # <add more features>
        return features
        
        


    @classmethod
    def parseArtefacts(cls, segments):
        edges = [ Edge(segments[i:i+2]) for i in range(len(segments) - 1) ]
        # triades
        allTriades = set([ a+b+c for a in "FSR" for b in "FSR" for c in "FSR"])
        triadesNotEdge = {"FFF", "FFR", "FFS", "RRF", "RRR", "RRS", "SSF", "SSR", "SSS"}
        triadesIsEdge = allTriades - triadesNotEdge

        # fill artefact fuzzy matrix
        artefacts = [ Artefact() ]
        for i in range(1,len(edges)-1):

            triade = dict()
            scoreEdge, scoreNotEdge = 0, 0
            for key in allTriades:
                value = fuzzy.AND(edges[i-1].getKhi(key[0]),
                                        edges[i].getKhi(key[1]),
                                        edges[i+1].getKhi(key[2]) )
                if key in triadesIsEdge:
                    scoreEdge = fuzzy.OR(scoreEdge, value)
                else:
                    scoreNotEdge = fuzzy.OR(scoreNotEdge, value)
                triade[key] = value
            edges[i].fuzzyScore = triade

            # score for edge (normalized to 100)
            edgeScore = scoreEdge/(scoreEdge+scoreNotEdge)

            artefacts[-1].append(edges[i].first)
            if edgeScore >= 0.5:
                artefacts.append(Artefact())
            

        return artefacts
        








