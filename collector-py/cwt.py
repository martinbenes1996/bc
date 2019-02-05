#!/usr/bin/env python3

import sys
import time
import scipy.signal as signal
import numpy as np
import matplotlib.pyplot as plt
import pywt
import math


class Transformer:
    """ Transforms signal to CWT coefficients. """
    def __init__(self):
        self.widths = np.arange(1,31)
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111)
        self.ax.set_xlabel("Samples")
        self.ax.set_ylabel("Frequency")
        self.ax.set_ylim(1,31)
        self.cb = None
        #self.ax.set_yscale('log', basey=10)
        self.x, self.y = np.meshgrid(np.arange(0,240), np.logspace(np.log10(self.widths[-1]), np.log10(self.widths[0]), np.size(self.widths)))
        self.cwtcnt = np.size(self.x,1)
        #plt.pause(10e-9)

#def sig2energy(x):
#    #m = np.absolute(x)
#    l = np.size(x,1)
#    print("size", l)
#    return x*x / l

    @staticmethod
    def crop(x,y):
        leftUntil = 110
        rightFrom = 130
        topLimit = 33
        c = (topLimit/(240-rightFrom))
        return (y < (-topLimit/leftUntil)*x + topLimit) or (y < c*x - c*rightFrom)

    def generateScalogram(self, m):
        rCnt = np.size(m, 1)
        cCnt = np.size(m, 0)
        m = np.flip(m,0)
        for r in range(0,rCnt):
            for c in range(0,cCnt):
                if self.crop(r,c):
                    m[c,r] = 0
        m = np.flip(m,0)
        m = 100 * np.abs(m**2) / np.sum(m)
        return m


    def process(self, x, show=False):
        cwtmatr = signal.cwt(x, signal.ricker, self.widths)
        #cwtmatr,fq = pywt.cwt(x, self.widths, 'morl')

        if show:
            scalogram = self.generateScalogram(cwtmatr)
            
            c = self.ax.pcolormesh(self.x, self.y, scalogram, cmap='PRGn', vmin=-50, vmax=50)
            if self.cb != None:
                self.cb.remove()
            self.cb = self.fig.colorbar(c)
            plt.pause(10e-9)
            
            
        



