
import csv
import numpy as np
import sys

import matplotlib.pyplot as plt

sys.path.insert(0, '.')
import comm_replay
import conf
import model
import segment

i = 0
status = True
def test(s1, s2, acc = 0.0001):
    global status
    global i
    i += 1
    d = abs(s1 - s2)
    
    if d > acc:
        if status:
            print("")
        print(str(i)+": "+str(s1)+" != "+str(s2)+".", file=sys.stderr)
        status = False


def testGenerator(mu,var):
    x = np.random.normal(mu,var, 1000000)
    s = segment.Segment(x)
    test(s.mu(), mu)
    test(s.var(), var)


def testExtraction(name):
    # read signal
    x = comm_replay.Reader.readFile(name)
    # extract features
    features = model.Extractor.extract(x)

    #print("Features:", features)

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
def sign(x):
    if x > 0:
        return 1
    elif x < 0:
        return -1
    else:
        return 0
def testRegression():
    lr = model.LinearRegression()
    lr.addTrainData([1,1], True)
    lr.addTrainData([1,0], True)
    lr.addTrainData([0,1], True)
    
    lr.addTrainData([-1,-1], False)
    lr.addTrainData([-1,0], False)
    lr.addTrainData([0,-1], False)

    lr.train()

    test( sign(lr.classify([2,2])), 1 )
    test( sign(lr.classify([3,4])), 1 )

    test( sign(lr.classify([-1,-0.5])), -1 )
    test( sign(lr.classify([-0.5,-1])), -1 )

def testClassification():
    model.Classification.setTrainSet(['c4m_LR_1','c4m_RL_1','c5m_LR_1','c5m_RL_1'])
    model.Classification.setTestSet(['c4m_LR_1', 'c4m_RL_1'])
    c = model.Classification.getTrained()
    result = c.test(['c4m_LR_1'])
    #print(result)

def testClassification2():
    # get classifiers
    c = model.Classification.getTrained()
    # get artefacts
    x = comm_replay.Reader.readFile(name)
    artefacts = segment.Artefact.parseArtefacts(x)
    for a in artefacts:
        m = c.classify(a.getFeatures)
        print(m)

def main():
    #conf.Config.setDebug(False)

    #testExtraction("../data/c4m_RL_1/c4m_RL_1_2.csv")

    #testRegression()

    #testClassification()
     
    testClassification2()
    
    assert(status)





if __name__ == '__main__':
    main()
