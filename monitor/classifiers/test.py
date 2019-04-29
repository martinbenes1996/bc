
import numpy as np
import sys

import matplotlib.pyplot as plt

sys.path.insert(0, '.')
import model


class Tester:

    def plotTest(self, key):
        # train
        c = model.Classification.getTrained()
        # test
        results = c.test()
        for testname,result in results.items():
            if len(result) == 1:
                print(result)
                result = result * 2
            # x,y
            x = np.linspace(0,len(result),len(result))
            y = [i[key][0] for i in result]
            y_ref = [1 if i[key][1] else 0 for i in result]
            print(testname)
            # plot
            plt.plot(x,y,c='r')
            plt.plot(x,y_ref,c='k')
            plt.show()


def main():
    tester = Tester()
    tester.plotTest('distance')
   
    


if __name__ == '__main__':
    main()
