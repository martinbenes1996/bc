#!/usr/bin/env python3

import csv
import socket
import sys
import time
import scipy.signal as signal
import numpy as np
import matplotlib.pyplot as plt
import pywt
import math

#if len(sys.argv) == 3 and sys.argv[1] == '-f':
#    filename = sys.argv[2]
#else:
#    filename = 'file.dat'

#f = open(filename, 'rb')
#data = f.read()

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
sock.bind( (("127.0.0.1", 5005)) )

widths = np.arange(1,31)

fig = plt.figure()
ax = fig.add_subplot(111)
x,y = np.meshgrid(np.arange(0,240), np.logspace(np.log10(widths[-1]), np.log10(widths[0]), np.size(widths)))
cwtcnt = np.size(x,1)
plt.pause(10e-9)

def sig2energy(x):
    #m = np.absolute(x)
    l = np.size(x,1)
    print("size", l)
    return x*x / l

def leftEdge(x):
    #return (1 / math.tan(math.radians(x/1.8)) - 0.9)**2#**1.75
    return (1 / math.tan(math.radians(x/1.8)) - 0.9)**2
def rightEdge(x):
    return (math.tan(math.radians((x-180)*1.5))+0.8)**2#**2.15
def crop(x,y):
    if x <= 0 or x >= 240:
        return True
    elif x < 60:
        return leftEdge(x) > y
    elif x > 180:
        return rightEdge(x) > y
    else:
        return False

def crop2(x,y):
    leftUntil = 110
    rightFrom = 130
    topLimit = 33
    c = (topLimit/(240-rightFrom))
    return (y < (-topLimit/leftUntil)*x + topLimit) or (y < c*x - c*rightFrom)

while True:
    msg = sock.recv(500)
    name = msg[0:msg.find(b'\0')].decode("utf-8")
    data = msg[msg.find(b'\0')+1:]

    l = np.array([int.from_bytes(data[i:i+2],byteorder='big') for i in range(0,len(data)-1,2)])


    print("Received", len(l), "samples from", name)

    cwtmatr = signal.cwt(l, signal.ricker, widths)

    cwt_rowcnt = np.size(cwtmatr, 1)
    cwt_colcnt = np.size(cwtmatr, 0)
    cwtmatr = np.flip(cwtmatr,0)

    for r in range(0,cwt_rowcnt):
        for c in range(0,cwt_colcnt):
            i,j = cwt_rowcnt-r-1, cwt_colcnt-c-1
            if crop2(r,c):
                cwtmatr[c,r] = 0
    
    cwtmatr = np.flip(cwtmatr,0)

    ax.pcolormesh(x, y, np.abs(cwtmatr)**2 / cwtcnt, cmap='PRGn')
    ax.set_xlabel("Samples")
    ax.set_ylabel("Frequency")
    #ax.set_yscale('log', basey=10)
    ax.set_ylim(1,31)

    #cwtmatr = sig2energy(cwtmatr)
    #m = np.absolute(cwtmatr)
    #print(m)
    #plt.imshow(m, extent=[1,240,1,31], cmap='PRGn', aspect='auto', vmax=m.max(), vmin=m.min())

    plt.pause(10e-9)



