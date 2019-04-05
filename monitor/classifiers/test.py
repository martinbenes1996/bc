
import numpy as np
import sys

import matplotlib.pyplot as plt

sys.path.insert(0, '.')
import model


class Tester:
    trainSet = ['3m_RL2']

    @staticmethod
    def normalize(l):
        return (np.array(l) - min(l)) / max(l)
    
    def plotTest(self, key):
        # train
        c = model.Classification.getTrained()
        # test
        results = c.test()
        for testname,result in results.items():
            # x,y
            x = np.linspace(0,len(result),len(result))
            y = [i[key][0] for i in result]
            y_ref = [1 if i[key][1] else 0 for i in result]
            y = self.normalize(y)
            # plot
            plt.plot(x,y,c='r')
            plt.plot(x,y_ref,c='k')
            plt.show()


def main():
    tester = Tester()
    tester.plotTest('presence')
   
    


if __name__ == '__main__':
    main()
