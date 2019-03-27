
import csv
import numpy as np
import sys

import matplotlib.pyplot as plt

sys.path.insert(0, '.')
import comm_replay
import model
import segment

def testEq(cmp,ref, key):
    dmin = 0.05
    d = abs(cmp - ref)
    if d > dmin:
        print(key + ":", ref, "!=", cmp, file=sys.stderr)
    assert(d <= dmin)

def testGenerator(mu,var):
    x = np.random.normal(mu,var, 1000000)
    s = segment.Segment(x)
    testEq(s.mu(), mu, "Mean")
    testEq(s.var(), var, "Variance")

def testEdges(name):
    x = comm_replay.Reader.readFile(name)
    segments = segment.Segment.segmentize(x)        
    replacer = [s.mu() for s in segments for _ in range(s.len())]

    plt.plot(x)
    plt.plot(replacer, c='r')
    plt.show()

def testObjects(name):
    # read signal
    x = comm_replay.Reader.readFile(name)
    segments = segment.Segment.segmentize(x)

    # segment segments
    artefacts = segment.Artefact.parseArtefacts(segments)

    k = []
    for a in artefacts:
        k.append(*a.getFeatures())



    #replacer = [s.mu() for s in segments for _ in range(s.len())]
    
    #plt.plot(x)
    #plt.plot(replacer, c='k')

    
    

    start = 0
    col = 'r'
    for i,a in enumerate(artefacts):
        y = a.samples()
        x = [start+i for i in range(len(y))]
        line = []
        it = y[0]
        for xi in x:
            line.append(it)
            it += xi * k[i] / abs(max(y) - min(y))
        
        plt.plot(x,y,c=col)
        plt.plot(x,line, c='k')
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
    testObjects("../data/6m_LR/6m_LR_2.csv")

    #testExtraction("../data/6m_RL/6m_RL_2.csv")



if __name__ == '__main__':
    main()
