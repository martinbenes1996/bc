#!/usr/bin/env python3

import csv
import socket
import sys
import time

if len(sys.argv) == 3 and sys.argv[1] == '-f':
    filename = sys.argv[2]
else:
    filename = 'file.dat'

f = open(filename, 'rb')
data = f.read()
l = [int.from_bytes(data[i:i+2],byteorder='big') for i in range(0,len(data)-1,2)]

with open(filename[:-4]+'.csv', 'w', newline='') as f:
    writer = csv.writer( f )
    writer.writerow( l )

print(filename, "saved into", filename[:-4]+'.csv')

