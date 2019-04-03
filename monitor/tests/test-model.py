
import csv
import numpy as np
import sys

import matplotlib.pyplot as plt

sys.path.insert(0, '.')
import comm_replay
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
    c = model.Classification.getTrained()
    c.test('3m_LR')



def main():
    #for m in range(0,10):
    #    testGenerator(m,m/1000.)

    testExtraction("../data/6m_RL/6m_RL_2.csv")
    #testArtefacts("../data/6m_RL/6m_RL_2.csv")

    testRegression()

    testClassification()

    assert(status)





if __name__ == '__main__':
    main()
