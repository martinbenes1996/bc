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

l = []
with open(filename, 'r') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    line_count = 0
    for row in csv_reader:
        if line_count == 1:
            l = [int(i) for i in row]
        else:
            for i in row[10:]:
                l.append(int(i))
        line_count += 1

print(l)
#l = [int.from_bytes(data[i:i+2],byteorder='big') for i in range(0,len(data)-1,2)]

fig = plt.figure()
ax = fig.add_subplot(111)
ax.plot(l, color='magenta')
ax.set_xlabel('samples')
ax.set_ylabel('signal')

#lines = plt.legend().get_lines()
#plt.setp(lines, linewidth='1')

#plt.ylim(0,1027)
plt.show()
