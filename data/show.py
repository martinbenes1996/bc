#!/usr/bin/env python3

import csv
import socket
import sys
import time
import matplotlib.pyplot as plt
import numpy as np


if len(sys.argv) == 3 and sys.argv[1] == '-f':
    filename = sys.argv[2]
else:
    filename = 'file.dat'

y = []
with open(filename, 'r') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    line_count = 0
    for row in csv_reader:
        if line_count == 1:
            y = [int(i) for i in row]
        else:
            for i in row[10:]:
                y.append(int(i))
        line_count += 1

x = [i/100. for i in range(0, len(y))]
#print(x)
#l = [int.from_bytes(data[i:i+2],byteorder='big') for i in range(0,len(data)-1,2)]

fig = plt.figure()
ax = fig.add_subplot(111)
ax.plot(x, y, color='magenta')
ax.set_xlabel('time [s]')
ax.set_ylabel('signal')
ax.set_ylim(0,1027)

#lines = plt.legend().get_lines()
#plt.setp(lines, linewidth='1')

#plt.ylim(0,1027)
#fig.savefig(filename[:-4]+".png")
#print("Generated:", filename[:-4]+".png")
plt.show()
