import serial
import time

time.sleep(3)
print("===")
ser = serial.Serial('COM4')
f = open('walk06.dat','wb')
for _ in range(0,1000):
    l = ser.readline()[:-2]
    i = int(l.decode('utf-8'))
    b = (i).to_bytes(2, byteorder='big')
    f.write(b)
f.close()

#with open('calm01.dat','rb') as file:
#    fileContent = file.read()
#    print(fileContent)
    
        
