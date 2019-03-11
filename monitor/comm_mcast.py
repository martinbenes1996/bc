
import csv
import datetime
import socket
import struct
import sys
import _thread
import time

import comm
sys.path.insert(0, '../collector-py/')
import conf


class Reader(comm.Reader):
    """Reader of data from multicast. Singleton.
    
    Attributes:
        sockets
    """
    # socket instances
    _sockets = {}
    @classmethod
    def getReader(cls, key, port=None):
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
        """
        super().__init__()
        # create variables
        self.sock = sock
        # start reader thread
        _thread.start_new_thread(self.read, ())

    
    def getSegment(self):
        """Gets segment."""
        # reader not started
        if not self.started:
            print("No data received.", file=sys.stderr)
            segmentN = conf.Config.segment()[0]
            return [0 for _ in range(0,segmentN)]
        # multithread access
        with self.segmentLock:
            return self.segment

    

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
        try:
            packet,addr = self.sock.recvfrom(1024)
        # no connection
        except socket.timeout as e:
            print("Comm.MCastClient: no update received, empty data generated.")
            return []
        

        # parse data
        data = struct.unpack('i'*int(len(packet)/4), packet)

        print("Comm.MCastClient: received update from ", addr)
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
                print("Recording to", self.filename, "ended.")
                self.filename = ''
                return
            # generate name
            filename = "PIR " + str(datetime.datetime.now()) + ".csv"
        # start recording
        self.filename = filename
        print("Recording to", self.filename, "started.")
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
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        try:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        except AttributeError:
            pass
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 32)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 1)

        sock.bind(('', port))
        host = socket.gethostbyname(socket.gethostname())
        sock.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_IF, socket.inet_aton(host))
        mreq = struct.pack('4sL', socket.inet_aton(addr), socket.INADDR_ANY)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        #sock.settimeout(1)
        return sock

    @classmethod
    def compile(cls, host, port):
        return ((host, port))
    @classmethod
    def hash(cls, host, port):
        return str(cls.compile(host, port))
    
        
