#!/usr/bin/env python3

import socket
import sys
import time


def proc2Args(l):
    if l[0] == '-d':
        return 'file.dat',l[1]
    elif l[0] == '-f':
        return l[1],'center'
    else:
        raise Exception('Invalid parameters.')

def proc4Args(arg):
    f,d = proc2Args(arg[1:3])
    if arg[1] == '-f':
        _,d = proc2Args(arg[3:])
        if arg[3] == '-f':
            raise Exception('Invalid parameters.')
    else:
        f,_ = proc2Args(arg[3:])
        if arg[3] == '-d':
            raise Exception('Invalid parameters.')
    return f,d

def procArgs(arg):
    if len(sys.argv) == 3:
        f,d = proc2Args(arg[1:])
    elif len(sys.argv) == 5:
        f,d = proc4Args(arg[1:])
    else:
        raise Exception('Invalid parameters.')
    return f,d

filename,device = procArgs(sys.argv)

f = open(filename, 'rb')
data = f.read()
end = len(data)
data = data[0:end]

segments = [data[i:i+120] for i in range(0,end-120+1,100)]

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)  
for segment in segments:
    #print(int.from_bytes(segment[0:2], byteorder='big'))

    sock.sendto(b"center\0"+segment, ("127.0.0.1", 5005))
    print("Replay: sent", len(b"center\0"+segment),"B.")
    time.sleep(0.5)