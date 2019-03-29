

"""
File:           comm_mcast.py
Author:         Martin Benes
Institution:    Faculty of Information Technology
                Brno University of Technology

This module contains classes enabling program to receive data via multicast.
Developed as a part of bachelor thesis "Counting of people using PIR sensor".
"""

import csv
import datetime
import socket
import struct
import _thread
import time

import comm


class Reader(comm.Reader):
    """Reader of data from multicast. Singleton.
    
    Attributes:
        sockets     Reader instances for various channels.
        sock        Socket for reading multicast channel.
    """
    # Reader instances (singletons)
    _sockets = {}
    @classmethod
    def getReader(cls, key, port=None):
        """Instance getter (singleton).

        Arguments:
            key     Host or (host,port).
            port    Port. If not None, key is host.
        """
        if port:
            host = key
            key = cls.hash(host, port)
        else:
            host,port = eval(key)
        if key in cls._sockets:
            rdr = cls._sockets[key]
        else:
            host,port = eval(key)
            sock = cls.createMCastSocket(host, port)
            cls._sockets[key] = rdr = cls(sock)
        return rdr


    def __init__(self, sock):
        """Constructs object.
        
        Arguments:
            sock        Socket.
        """
        super().__init__()
        # create variables
        self.sock = sock
        # start reader thread
        _thread.start_new_thread(self.read, ())

    def read(self):
        """Reads multicast channel. Done in separated thread."""
        i = 0
        while True:
            i += 1
            # read
            s = self.readSegment()
            with self.segmentLock:
                self.segment = s
                #self.setStatus("Update received.")
                #print("Reader: Read ", i)

            # record
            self.write(s)
            # indicate change
            self.indicate(True)
            self.started = True
            # wait 300 ms
            time.sleep(0.3)

    def readSegment(self):
        """Reads single segment from socket."""
        try:
            packet,addr = self.sock.recvfrom(1024)
        # no connection
        except socket.timeout as e:
            print("Comm.MCastClient: no update received, empty data generated.")
            return []
        # parse data
        data = struct.unpack('i'*int(len(packet)/4), packet)
        #print("Comm.MCastClient: received update from ", addr)
        return data
    
    def record(self, filename=None):
        """Controls recording.
        
        Arguments:
            filename    Filename of file to save recording to.
        """
        # filename not given or ""
        if not filename:
            # stop recording
            if self.filename:
                #print("Recording to", self.filename, "ended.")
                self.filename = ''
                return
            # generate name
            filename = "PIR " + str(datetime.datetime.now()) + ".csv"
        # start recording
        self.filename = filename
        #print("Recording to", self.filename, "started.")
        f = open(self.filename, 'w')

    def write(self, segment):
        """Saves segment to file.
        
        Arguments:
            segment     Segment to save.
        """
        # recording turned off
        if not self.filename:
            return
        # save segment
        with open(self.filename, "a", newline='') as f:
            csvwriter = csv.writer(f)
            csvwriter.writerow(segment)
    

    @classmethod
    def createMCastSocket(cls, addr, port):
        """Creates multicast socket.
        
        Arguments:
            addr        Multicast group address.
            port        Multicast group port.
        """
        # create socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        # set socket options
        try:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        except AttributeError:
            pass
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 32)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 1)
        # bind
        sock.bind(('', port))
        # set socket to interface
        host = socket.gethostbyname(socket.gethostname())
        sock.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_IF, socket.inet_aton(host))
        # mreq
        mreq = struct.pack('4sL', socket.inet_aton(addr), socket.INADDR_ANY)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        #sock.settimeout(1)
        return sock

    @classmethod
    def compile(cls, host, port):
        """Compile host and port into structure.
        
        Arguments:
            host        Host address.
            port        Port.
        """
        return ((host, port))
    @classmethod
    def hash(cls, host, port):
        """Hash host and port into key, used to save the pair under.
        
        Arguments:
            host        Host address.
            port        Port.
        """
        return str(cls.compile(host, port))
    

# called directly
if __name__ == '__main__':
    from globals import *
    raise NotCallableModuleError