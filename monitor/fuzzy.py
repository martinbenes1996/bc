
import math

class TriangularSet:
    def __init__(self, width=1, xcenter=0, infiniteSide=None):
        assert(width > 0)
        assert( infiniteSide in {"L","R",None} )
        self.left = lambda x : (x-xcenter)/width + 1
        self.leftBorder = (xcenter-width, xcenter)
        self.right = lambda x : -(x-xcenter)/width + 1
        self.rightBorder = (xcenter, xcenter+width)
        
        
        self.orientation = infiniteSide
            
    def getLeftInfinite(self, x):
        if x >= self.rightBorder[1]:
            return 0
        elif x >= self.rightBorder[0]:
            return self.right(x)
        else:
            return 1
    def getRightInfinite(self, x):
        if x <= self.leftBorder[0]:
            return 0
        elif x <= self.leftBorder[1]:
            return self.left(x)
        else:
            return 1
    def getTriangle(self, x):
        if x >= self.leftBorder[0] and x <= self.leftBorder[1]:
            return self.left(x)
        elif x >= self.rightBorder[0] and x <= self.rightBorder[1]:
            return self.right(x)
        else:
            return 0

    def get(self, x):
        if self.orientation == "L":
            return self.getLeftInfinite(x)
        elif self.orientation == "R":
            return self.getRightInfinite(x)
        else:
            return self.getTriangle(x) 

class ArctangenoidSet:
    def __init__(self, width=1, xcenter=0, side="L"):
        assert(width > 0)
        assert( side in {"L","R"} )
        if side == 'L':
            self.f = lambda x : math.atan( 4*(-x-xcenter-width)/width ) / math.pi + 0.5
        elif side == 'R':
            self.f = lambda x : math.atan( 4*(x-xcenter-width)/width ) / math.pi + 0.5
            

    def get(self, x):
        #print(x, self.xcenter)
        return self.f(x)

class GaussianSet:
    def __init__(self, width=1, xcenter=0):
        assert(width > 0)
        mu = xcenter
        var = width
        self.f = lambda x : math.sqrt(math.exp(-((mu-x)**2)/(2*(0.6*var)**2)))

    def get(self, x):
        return self.f(x)
