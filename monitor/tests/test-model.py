
import csv
import numpy as np
import sys

import matplotlib.pyplot as plt

sys.path.insert(0, '.')
import comm_replay
import model

def testEq(cmp,ref, key):
    dmin = 0.05
    d = abs(cmp - ref)
    if d > dmin:
        print(key + ":", ref, "!=", cmp, file=sys.stderr)
    assert(d <= dmin)

def testGenerator(mu,var):
    x = np.random.normal(mu,var, 1000000)
    testEq(model.mu(x), mu, "Mean")
    testEq(model.var(x), var, "Variance")

def testEdges(name):
    x = comm_replay.Reader.readFile(name)

    coefs = model.waveletTransformation(x)
    edges = model.edges(x)

    segments = model.segmentize(x)
    mus = model.segMus(segments)

    # merging segments
    #while True:
    #    mergescore = np.array([(mus[i+1] - mus[i])*(mus[i+2] - mus[i+1]) for i in range(len(mus)-2)])
    #    print(mergescore)
    #    if mergescore.max() < 10000:
    #        break
    #    index = np.argmax(mergescore)
    #
    #    print("Score", mergescore[index], "Merging", mus[index], mus[index+1], mus[index+2])
    #
    #    segments[index] = np.concatenate([segments[index],segments[index+1],segments[index+2]])
    #    segments = np.concatenate([segments[:index+1],segments[index+3:]])
    #    #del segments[index+2]
    #    #del segments[index+1]
    #    mus = model.segMus(segments)

        
    replacer = []
    for it,b in enumerate(model.segBorders(x)):
        for segIt in range(b[0],b[1]):
            replacer.append(mus[it])
    replacer = np.array(replacer)
    
    #l = 0
    #xmus = []
    #for seg in segments:
    #    xmus.append(l + np.size(seg)/2)
    #    l += np.size(seg)
    #xmus = np.array([ model.mu(seg) for seg in segments])
    xmus = np.array([ model.mu(b) for b in model.segBorders(x)])



    
    plt.plot(x)
    plt.plot(replacer, c='r')
    #plt.scatter(xmus,mus,s=50, c='r')

    #plt.scatter(edges,x[edges],s=20, c='r')
    plt.show()

def testObjects(name):
    # read signal
    x = comm_replay.Reader.readFile(name)
    segs = model.segmentize(x)
    segmus = model.segMus(segs)
    segstarts = model.segStarts(segs)
    #print(segstarts)

    # segment segments
    objectborders = model.objectBorders(segs)
    objectsegments = model.objectSegments(segs)
    print(objectborders)

    mus = model.segMus(segs)
    replacer = []
    for it,b in enumerate(model.segBorders(x)):
        for segIt in range(b[0],b[1]):
            replacer.append(mus[it])
    replacer = np.array(replacer)
    #plt.plot(replacer, c='k')

    
    

    start = 0
    col = 'r'
    for i,objsegs in enumerate(objectsegments):
        l = model.segLens(objsegs)
        y = np.concatenate(objsegs)
        x = [start+i for i in range(len(y))]
        plt.plot(x,y,c=col)
        if col == 'r':
            col = 'g'
        elif col == 'g':
            col = 'b'
        elif col == 'b':
            col = 'y'
        elif col == 'y':
            col = 'c'
        elif col == 'c':
            col = 'm'
        else:
            col = 'r'
        start += np.size(y)
    plt.show()
    
    #plt.plot(x)
    #x = [ segstarts[o[0]] for o in objectborders ]
    #y = [ segmus[o[0]] for o in objectborders ]
    #plt.scatter(x,y,s=50,c='r')
    #plt.show()



def testExtraction(name):
    # read signal
    x = comm_replay.Reader.readFile(name)
    # extract features
    f = model.Extractor.extract(x)

    print("Features:", f)

    



def main():
    #for m in range(0,10):
    #    testGenerator(m,m/1000.)
    #testEdges("../data/6m_RL/6m_RL_2.csv")
    testObjects("../data/6m_RL/6m_RL_2.csv")

    #testExtraction("../data/6m_RL/6m_RL_2.csv")



if __name__ == '__main__':
    main()
