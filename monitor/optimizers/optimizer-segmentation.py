
import csv
import numpy as np
import os
import re
import sys

import matplotlib.pyplot as plt

sys.path.insert(0, '.')
import comm_replay
import model
import segment

def getVarianceSum(segments):
    varSum = 0
    for seg in segments:
        varSum += seg.var()
    return varSum

def getOptimum(name):
    x = comm_replay.Reader.readFile(name)

    data = []
    coefSpace,edgeSpace = np.linspace(0.1,10,100),range(1,20)
    processPercent = -1
    for i,cwtCoef in enumerate(coefSpace):
        row = []
        for edgeOrder in edgeSpace:
            model.cwtCoef,model.edgeOrder = cwtCoef,edgeOrder
            

            segments = segment.Segment.segmentize(x)    
            varSum = getVarianceSum(segments)

            row.append(varSum)

        data.append(row)
        processNow = int((i+1)/len(coefSpace) * 100)
        if processPercent < processNow:
            processPercent = processNow
            print('\r', end='')
            print(processPercent, "%", end='')
    print("")
    data = np.array(data)

    # optimum
    optimum_x,optimum_y = np.where(data == data.min())
    optimum = edgeSpace[optimum_x[0]],coefSpace[optimum_y[0]]

    # paint
    #x,y = np.meshgrid(edgeSpace,coefSpace)
    #fig,ax = plt.subplots()
    #zmin,zmax = -np.abs(data).min(),np.abs(data).max()
    #c = ax.pcolormesh(x,y,data, cmap='RdBu', vmin=zmin, vmax=zmax)
    #ax.axis([x.min(), x.max(), y.min(), y.max()])
    #fig.colorbar(c)
    #ax.scatter(optimum[0], optimum[1], s=50, c='g')
    #plt.show()

    return optimum
    

def optimize():
    optimums = {}
    dirs = [ "../data/"+d for d in model.Classification.getTrainSet()]
    files = [d+'/'+f for d in dirs for f in os.listdir(d) if re.match(r".*\.csv",f)]

    for i,f in enumerate(files):
        print(i+1,"/",len(files))
        optimums[f] = getOptimum(f)
    
    optimalEdge = np.mean([item[0] for item in optimums.values()])
    optimalCwt = np.mean([item[1] for item in optimums.values()])
    print("Optimal edge order:", optimalEdge)
    print("Optimal CWT coefficient:", optimalCwt)



def main():
    optimize()



if __name__ == '__main__':
    main()
