#!/usr/bin/env python3

import math
import numpy as np
import pywt
import scipy.signal as signal
import sys
import time

import conf

class Transformer:
    """ Transforms signal to CWT coefficients. """

    @staticmethod
    def crop(x,y):
        leftUntil = 105
        rightFrom = 135
        topLimit = 33
        c = (topLimit/(240-rightFrom))
        return (y < (-topLimit/leftUntil)*x + topLimit) or (y < c*x - c*rightFrom)

    def postprocess(self, m):
        rCnt = np.size(m, 1)
        cCnt = np.size(m, 0)
        m = np.flip(m,0)
        for r in range(0,rCnt):
            for c in range(0,cCnt):
                if self.crop(r,c):
                    m[c,r] = 0
        m = np.flip(m,0)
        #m = 100 * np.abs(m**2) / np.sum(m)
        return m


    def process(self, x):
        # CWT
        cwtmatr = signal.cwt(x, signal.ricker, conf.Config.cwtCoefs())
        #cwtmatr,fq = pywt.cwt(x, conf.Config.cwtCoefs(), 'morl')

        return self.postprocess(cwtmatr)
        
            
            
        



