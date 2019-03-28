
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




def testExtraction(name):
    # read signal
    x = comm_replay.Reader.readFile(name)
    # extract features
    features = model.Extractor.extract(x)

    print("Features:", features)

def testArtefacts(name):
    # read signal
    x = comm_replay.Reader.readFile(name)
    # get artefacts
    artefacts = segment.Artefact.parseArtefacts(x)

    col = 'orange'
    start = 0
    for i,a in enumerate(artefacts):
        y = a.samples()
        N = len(y)
        x = [start+j for j in range(N)]
        line = a.getFeatures(plotting=True)

        plt.plot(x,y,c=col)
        plt.plot(x,line,c='k')

        if col == 'orange':
            col = 'r'
        elif col == 'r':
            col = 'yellow'
        else:
            col = 'orange'
        start += N
    plt.show()


    #print("Features:", features)
    



def main():
    #for m in range(0,10):
    #    testGenerator(m,m/1000.)

    testExtraction("../data/6m_RL/6m_RL_2.csv")
    #testArtefacts("../data/6m_RL/6m_RL_2.csv")


if __name__ == '__main__':
    main()
