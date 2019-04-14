#!/usr/bin/env python3

import csv
import json
import os
import socket
import sys
import time
import matplotlib.pyplot as plt
import numpy as np


assert(len(sys.argv) == 2)
filename = sys.argv[1]

y = []
with open(filename, 'r') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    line_count = 0
    for row in csv_reader:
        if line_count == 0:
            y = [int(i) for i in row]
        else:
            for i in row[10:]:
                y.append(int(i))
        line_count += 1

x = [i/100. for i in range(len(y))]
#print(x)
#l = [int.from_bytes(data[i:i+2],byteorder='big') for i in range(0,len(data)-1,2)]

with open( os.path.dirname(filename)+"/label.json", "r" ) as f:
    labeldata = json.load(f)

segments = labeldata[ os.path.basename(filename)[:-4] ]






fig = plt.figure()
ax = fig.add_subplot(111)
ax.plot(x, y, color='magenta')

y_ref = []
x_ref = []
for k in segments:
    for v in range(k['start'],k['start']+k['length']):
        if k['key'][0] == False:
            y_ref.append(0)
            x_ref.append(v/100.)
        elif k['key'][0] == True:
            y_ref.append(600)
            x_ref.append(v/100.)
ax.plot(x_ref,y_ref, color='k')


ax.set_xlabel('time [s]')
ax.set_ylabel('signal')
ax.set_ylim(0,1027)

#lines = plt.legend().get_lines()
#plt.setp(lines, linewidth='1')

#plt.ylim(0,1027)
#fig.savefig(filename[:-4]+".png")
#print("Generated:", filename[:-4]+".png")
plt.show()
