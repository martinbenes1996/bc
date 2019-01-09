
import socket
import struct

class Client:
    def __init__(self):
        """Client constructor."""
        print("Comm.Client: Initialize")
        self.sockets = dict()
    
    def __del__(self):
        """Client destructor."""
        # close all sockets
        for k,s in self.sockets.items():
            print("Comm.Client: Closing socket " + str(s.getpeername()) )
            s.close()
    
    def connect(self, id, host, port):
        """Creates new connection.
        
        Keyword arguments:
        id   -- id of created connection
        host -- host domain name / ip address
        port -- port to connect to
        """
        print("Comm.Client: Connect to " + str((host,port)) )
        # create connection
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect( ((host, port)) )
        # save connection
        self.sockets[ hash(id) ] = s
    
    def getServer(self):
        # receive socket
        sockRcvUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sockRcvUDP.bind(('', 0))
        host,port = sockRcvUDP.getsockname()
        print("Comm.Client: Receive UDP socket "+str((host,port)) )

        # send BCast socket
        sockBCast = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sockBCast.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        # send request
        msg = b'COMM HELLO ' + (port).to_bytes(2, byteorder='big')
        print(msg)
        sockBCast.sendto(msg, ('255.255.255.255',12345))
        sockBCast.close()

        # receive server address
        data,addr = sockRcvUDP.recvfrom(1024)
    
    def receive(self, id, size=100):
        """Receives data.
        
        Keyword arguments:
        id   -- id of connection sending the data
        """
        return self.sockets[hash(id)].recv(size)

class MCastClient:
    def __init__(self):
        """Multicast client constructor."""
        print('Comm.MCastClient: Initialize')
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        try:
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        except AttributeError:
            pass
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 32)
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 1)
        
        self.sock.bind(('', 12345))
        host = socket.gethostbyname(socket.gethostname())
        self.sock.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_IF, socket.inet_aton(host))
        mreq = struct.pack('4sL', socket.inet_aton('224.0.0.128'), socket.INADDR_ANY)
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

        self.sock.settimeout(1)
        
    
    def receive(self):
        try:
            data, addr = self.sock.recvfrom(1024)
        
        # no connection
        except socket.timeout as e:
            print("Comm.MCastClient: no update received, empty data generated.")
            return 0,[]
        
        # parse data
        count = struct.unpack('i', data[0:4])[0]
        if count > 0:
            seqdata = struct.unpack('ii'*count, data[4:])
            data = [(seqdata[i],seqdata[i+1]) for i in range(0, len(seqdata), 2)]
        else:
            data = []

        print("Comm.MCastClient: received update from ", addr)
        return len(data), data

    

    

