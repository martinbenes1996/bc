#!/usr/bin/env python3

import numpy as np
import socket

class Client:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
        self.sock.bind( (("127.0.0.1", 5005)) )
    
    def get(self):
        msg = self.sock.recv(500)
        name = msg[0:msg.find(b'\0')].decode("utf-8")
        data = msg[msg.find(b'\0')+1:]
        l = np.array([int.from_bytes(data[i:i+2],byteorder='big') for i in range(0,len(data)-1,2)])
        print("Received", len(l), "samples from", name)
        return l