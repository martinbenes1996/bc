

import numpy as np
import sys

import matplotlib.pyplot as plt

sys.path.insert(0, '.')
import fuzzy

class SetViewer:
    colors = ['r','b','g','c','m','y','k']
    colorIterator = 0
    xmin,xmax = -50,50
    x = np.linspace(xmin,xmax, 20*(xmax-xmin))

    def __init__(self, f):
        plt.xlim(self.xmin,self.xmax)
        plt.ylim(-0.1, 1.1)
        self.y = self.createY(f)
    
    @classmethod
    def createY(self, f):
        y = np.array([ f(xi) for xi in self.x])
        return y        


    def addToView(self):
        plt.plot(self.x, self.y, c=self.getColor())
    
    @classmethod
    def getColor(cls):
        c = cls.colors[cls.colorIterator]
        cls.colorIterator += 1
        if cls.colorIterator >= len(cls.colors):
            cls.colorIterator = 0
        return c
    
    
    
    @classmethod
    def show(cls):
        plt.show()


def main():
    SetViewer( fuzzy.GaussianSet(10).get ).addToView()
    SetViewer( fuzzy.ArctangenoidSet(10,0,"L").get ).addToView()
    SetViewer( fuzzy.ArctangenoidSet(10,0,"R").get ).addToView()

    SetViewer.show()



if __name__ == '__main__':
    main()
