
import datetime
import serial
import time
import sys


devname = '/dev/ttyS3'
print("Recorder launched")
ser = serial.Serial(devname)
print("Reading from", devname, '...')

time.sleep(3)

with open(sys.argv[1],'wb') as f:
    for i in range(0,1010):
        l = ser.readline()[:-2]
        i = int(l.decode('utf-8'))
        b = (i).to_bytes(2, byteorder='big')
        f.write(b)
        time.sleep(0.01)

        if (i % 100) == 0:
            print('\r', end='')
            print(datetime.timedelta(seconds=i/100), end='')
    
        
