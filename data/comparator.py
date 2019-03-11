
import csv
import sys
import matplotlib.pyplot as plt
import numpy as np

file1,file2 = sys.argv[1],sys.argv[2]

def readFile(name):
    #print("Read file", name)
    with open(name,'r') as f1:
        rd1 = csv.reader(f1, delimiter=',')
        data = []
        for line in rd1:
            for sample in line:
                data.append( int(sample) )
    return data

data1 = readFile(file1)
data2 = readFile(file2)

size = min(len(data1),len(data2))
data1 = data1[:size]
data2 = data2[:size]

mu1, mu2 = np.mean(data1), np.mean(data2)

maxscore, bestshift = 0, None 
for s in range(0,500):
    # compute
    score1, score2 = 0,0
    for i in range(s,size):
        score1 += (data1[i] - mu1)*(data2[i-s] - mu2)
        score2 += (data1[i-s] - mu1)*(data2[i] - mu2)
    
    # check1
    if abs(score1) > abs(maxscore):
        #print("1 - Replace score", str(maxscore), "with better score", str(score1))
        bestshift = s
        maxscore = abs(score1)
    # check2
    if abs(score2) > abs(maxscore):
        #print("2 - Replace score", str(maxscore), "with better score", str(score2))
        bestshift = -s
        maxscore = abs(score2)
print("Max score", maxscore, "was for shift", bestshift)

if bestshift < 0:
    data1 = [mu1] * abs(bestshift) + data1
    data2 = data2 + [mu2] * abs(bestshift)
elif bestshift > 0:
    data1 = data1 + [mu1] * abs(bestshift)
    data2 = [mu2] * abs(bestshift) + data2

x = [i/100. for i in range(0, len(data1))]

#wt = csv.writer(sys.stdout)
#wt.writerow([file1, file2, int(maxscore)])

plt.plot(x, data1, x, data2)
#plt.set_xlabel('time [s]')
#plt.set_ylabel('signal')
#plt.set_ylim(0,1027)

plt.show()
