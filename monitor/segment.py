

"""
File:           segment.py
Author:         Martin Benes
Institution:    Faculty of Information Technology
                Brno University of Technology

This module contains classes preprocessing the signal and performing the feature extraction.
Developed as a part of bachelor thesis "Counting of people using PIR sensor".
"""

import numpy as np
import scipy.signal as signal

import fuzzy

class Segment:
    """Class performing segmentation.
    
    Static attributes:
        cwtCoef
        edgeOrder
    Attributes:
        pos
        samples
    """
    cwtCoef = 1.33846 # 1.3384615384615386
    edgeOrder = 8 # 7.564102564102564
    
    def __init__(self, samples, position):
        """Constucts the segment class.
        
        Arguments:
            samples
            position
        """
        self.samples = samples
        self.pos = position
    def __len__(self):
        """Returns the length of the segment."""
        return len(self.samples)
    def len(self):
        """Returns the length of the segment."""
        return len(self)
    def mu(self):
        """Returns the mean value of the segment."""
        return np.mean(self.samples)
    def var(self):
        """Returns the variance of the segment."""
        return np.var(self.samples)
    def position(self):
        """Position of the segment in the signal."""
        return self.pos
    def xcenter(self):
        """Index of center of the segment."""
        return int(self.pos + len(self)/2)

    @classmethod
    def segmentize(cls, x):
        """Segmentizes the signal.
        
        Arguments:
            x       Input signal.
        """
        # changes using CWT
        coefs = signal.cwt(x, signal.ricker, [cls.cwtCoef])[0]
        extrems = signal.argrelextrema(coefs, np.greater, order=cls.edgeOrder)[0]
        try:
            if extrems[0] != 0:
                extrems = np.concatenate(([0],extrems))
        except IndexError:
            extrems = np.concatenate(([0],extrems))
        try:
            if extrems[-1] != len(x) - 1:
                extrems = np.concatenate((extrems,[len(x) - 1]))
        except IndexError:
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
    """Class covering the Edge computation.
    
    Static attributes:
        toleranceStagnation     Coefficient of tolerance towards stagnation.
        toleranceCharacter      Coefficient of tolerance towards character.
        Khi                     Fuzzifying sets (left/fall, stagnate, right/rise)
    Attributes:
        first                   First segment of the edge.
        second                  Second segment of the edge.
        fuzzyScore              Fuzzy score.
    """
    toleranceStagnation = 20
    toleranceCharacter = 2
    Khi = { "F": fuzzy.ArctangenoidSet(toleranceStagnation, 0, "L").get,
            "S": fuzzy.GaussianSet(toleranceStagnation).get,
            "R": fuzzy.ArctangenoidSet(toleranceStagnation, 0, "R").get }

    def __init__(self, segments):
        """Constructs the edge.
        
        Arguments:
            segments            Segment vector.
        """
        self.first, self.second = segments[0], segments[1]
        self.fuzzyScore = dict()
    def Dmu(self):
        """Difference of mean values of segments."""
        return self.second.mu() - self.first.mu()
    def Dvar(self):
        """Difference of variances of segments."""
        return self.second.var() - self.first.var()

    def muScore(self):
        """Mean value score of edge."""
        return self.Dmu() #/ self.toleranceStagnation
    def varScore(self):
        """Variance score of edge."""
        return self.Dvar() #/ self.toleranceCharacter

    def stagnates(self):
        """Returns weather stagnates or not."""
        return abs(self.muScore()) <= 1
    def rises(self):
        """Returns weather rises or not."""
        return not self.stagnates() and self.Dmu() > 0
    def falls(self):
        """Returns weather falls or not."""
        return not self.stagnates() and self.Dmu() < 0

    def S(self):
        """Score of stagnation."""
        return self.Khi["S"](self.muScore())
    def R(self):
        """Score of rising."""
        return self.Khi["R"](self.muScore())
    def F(self):
        """Score of falling."""
        return self.Khi["F"](self.muScore())
    def getKhi(self, key):
        """Returns score.
        
        Attributes:
            key         "S" for stagnation, "R" for rising, "F" for falling.
        """
        assert(key in {"S","R","F"})
        return self.Khi[key](self.muScore())
    
    def stays(self):
        """Returns weather stays (by characteristics) or not."""
        return abs(self.varScore()) <= 1
    def wilds(self):
        """Returns weather wilds (by characteristics) or not."""
        return self.varScore() > 1
    def calms(self):
        """Returns weather calms (by characteristics) or not."""
        return self.varScore() < -1

    @classmethod
    def edgify(cls, segments):
        """Factory for edge.
        
        Arguments:
            segments        Segment vector.
        """
        return [ cls(segments[0:2]), cls(segments[1:3]), cls(segments[2:4]) ]


class Artefact:
    """Representation of Artefact - merge of segments.
    Represented by double-linked list.
    
    Attributes:
        segments        Segment vector.
        previous        Pointer to previous
        optimalK        Optimal scope.
        _samples        Sample vector.
    """

    def __init__(self):
        """Constructor of Artefact."""
        self.segments = []
        self.previous = None
        self.optimalK = None
        self._samples = None

    def append(self, segment):
        """Append segment to artefact.
        
        Arguments:
            segment
        """
        self.segments.append(segment)

    def setPreviousArtefact(self, prev):
        """Sets pointer to predecesor.
        
        Arguments:
            prev        Reference to new neighbor.
        """
        self.previous = prev

    def samples(self):
        """Returns sample vector."""
        if self._samples is not None:
            return self._samples
        artefactSamples = []
        for segment in self.segments:
            for sample in segment.samples:
                artefactSamples.append(sample)
        self._samples = np.array(artefactSamples)
        return self._samples
    def mu(self):
        """Returns mean value of artefact."""
        return np.mean(self.samples())
    def var(self):
        """Returns variance of artefact."""
        return np.var(self.samples())
    def len(self):
        """Returns length of artefact."""
        return len(self.samples())

    def getK(self):
        """Returns slope of replacing line."""
        if self.optimalK is not None:
            return self.optimalK
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
        self.optimalK = optimalK
        return optimalK

    def getFeatures(self, plotting=False):
        """Extracts the features of the artefact.
        
        Arguments:
            plotting        Returns the semiresults.
        """
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
        if self.previous is not None:
            previousK = self.previous.getK()
        else:
            previousK = optimalK
        if optimalK is None:
            optimalK = 0
        if previousK is None:
            previousK = 0
        self.optimalK = optimalK

        if plotting:
            return optimalLine

        # line slope
        features.append(optimalK)
        # difference from line
        features.append(bestScore)
        # previous line slope
        features.append(previousK)
        # variance of artefact
        features.append(var)
        # length of segment
        features.append(N)
        # mean value of artefact
        features.append(mu)
        # minimum of artefact
        #features.append(smin)
        # maximum of artefact
        #features.append(smax)
        # ...
        # <add more features>
        return features
    
    @classmethod
    def artefactLength(cls, features):
        """Returns length of artefact from features.
        
        Arguments:
            features        Input feature vector.
        """
        return features[4]
        
    @classmethod
    def parseArtefacts(cls, x):
        """Parses signal to artefacts.
        
        Arguments:
            x       Signal vector.
        """
        segments = Segment.segmentize(x)
        if len(segments) == 1:
            a = cls()
            a.append(segments[0])
            return [a]
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
            # fuzzy operators
            AND = fuzzy.SNorm.method('product')
            OR = fuzzy.TConorm.method('maximum')
            # check all combinations for triade
            for key in allTriades:
                value = AND(edges[i-1].getKhi(key[0]),
                            edges[i].getKhi(key[1]),
                            edges[i+1].getKhi(key[2]) )
                if key in triadesIsEdge:
                    scoreEdge = OR(scoreEdge, value)
                else:
                    scoreNotEdge = OR(scoreNotEdge, value)
                triade[key] = value
            edges[i].fuzzyScore = triade

            # score for edge (normalized to 100)
            edgeScore = scoreEdge/(scoreEdge+scoreNotEdge)

            artefacts[-1].append(edges[i].first)
            if edgeScore >= 0.5:
                artefacts.append(Artefact())
                artefacts[-1].setPreviousArtefact(artefacts[-2])
                
        if artefacts[-1].len() == 0:
            artefacts = artefacts[:-1]
        return artefacts
    
        











# called directly
if __name__ == '__main__':
    from globals import *
    raise NotCallableModuleError
    