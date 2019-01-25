#!/usr/bin/env python3

import socket
import sys
import time

if len(sys.argv) == 3 and sys.argv[1] == '-f':
    filename = sys.argv[2]
else:
    filename = 'file.dat'

f = open(filename, 'rb')
data = f.read()
data = data[0:len(data) - len(data)%480]

segments = [data[i:i+480] for i in range(0,len(data),480)]

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
for segment in segments:
    #print(int.from_bytes(segment[0:2], byteorder='big'))

    sock.sendto(b"center\0"+segment, ("127.0.0.1", 5005))
    print("Replay: sent", len(b"center\0"+segment),"B.")
    time.sleep(0.2)