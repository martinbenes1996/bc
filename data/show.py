#!/usr/bin/env python3

import socket
import sys
import time
import matplotlib.pyplot as plt
import numpy as np


if len(sys.argv) == 3 and sys.argv[1] == '-f':
    filename = sys.argv[2]
else:
    filename = 'file.dat'

f = open(filename, 'rb')
data = f.read() 

l = [int.from_bytes(data[i:i+2],byteorder='big') for i in range(0,len(data)-1,2)]

fig = plt.figure()
ax = fig.add_subplot(111)
ax.plot(l, color='magenta')
ax.set_xlabel('time')
ax.set_ylabel('signal')

plt.ylim(0,1027)
plt.show()
