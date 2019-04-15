

"""
File:           fuzzy.py
Author:         Martin Benes
Institution:    Faculty of Information Technology
                Brno University of Technology

This module contains classes implementing entities from fuzzy logic.
Developed as a part of bachelor thesis "Counting of people using PIR sensor".
"""

import math
import numpy as np

def fuzzify(x, descriptor):
    minimum,maximum = descriptor
    variance = maximum - minimum
    return (x - minimum) / variance

class FuzzyOperator:
    """General fuzzy operator.
    
    Attributes:
        f       Implementation.
    """
    # constructor
    def __init__(self, f):
        """Constructor.
        
        Arguments:
            f       Negator implementation.
        """
        self.f = f
    def get(self, *args):
        """Delegator."""
        return self.f(*args)

class Negator(FuzzyOperator):
    """Fuzzy negator."""
    # standard
    @staticmethod
    def standard(*args):
        """Standard negator.
        
        Arguments:
            x       Input fuzzy value.
        """
        assert(len(args) == 1)
        x = args[0]
        return 1 -  x
    # circle
    @staticmethod
    def circle(*args):
        """Circle negator.
        
        Arguments:
            x       Input fuzzy value.
        """
        assert(len(args) == 1)
        x = args[0]
        return np.sqrt(1 - np.square(x)) 
    # parabolic
    @staticmethod
    def parabolic(*args):
        """Parabolic negator.
        
        Arguments:
            x       Input fuzzy value.
        """
        assert(len(args) == 1)
        x = args[0]
        return 1 - np.square(x)
    @classmethod
    def method(cls, name):
        """Returns callable operator of chosen name.
        
        Arguments:
            name        Name of the operator: {'standard', 'circle', 'parabolic'}
        """
        if name == 'standard':
            return cls(cls.standard).get
        elif name == 'circle':
            return cls(cls.circle).get
        elif name == 'parabolic':
            return cls(cls.parabolic).get
        else:
            raise NotImplementedError

class SNorm(FuzzyOperator):
    """Fuzzy norms (conjunctions)."""
    @staticmethod
    def product(*args):
        """Product fuzzy s-norm (conjunction)
    
        Arguments:
            args        Sequence of operands.
        """
        # (a_1) * (a_2) * (a_3) * ... * (a_K)
        result = 1
        for a in args:
            result = result * a
        return result
    @classmethod
    def method(cls, name):
        """Returns callable operator of chosen name.
        
        Arguments:
            name        Name of the operator: {'product'}
        """
        if name == 'product':
            return cls(cls.product).get
        else:
            raise NotImplementedError

class TConorm(FuzzyOperator):
    """Fuzzy conorms (disjunctions)."""
    @staticmethod
    def maximum(*args):
        """Maximum fuzzy t-conorm (disjunction)
    
        Arguments:
            args        Sequence of operands.
        """
        # MAX( (a_1), (a_2), (a_3), ... , (a_K) )
        return max( args )
    @staticmethod
    def probsum(*args):
        """Probability sum fuzzy t-conorm (disjunction)
    
        Arguments:
            args        Sequence of operands.
        """
        # (a_1) + (a_2) - (a_1)(a_2), ...
        result = 0
        for a in args:
            result = result + a - result*a
        return result
    @classmethod
    def method(cls, name):
        """Returns callable operator of chosen name.
        
        Arguments:
            name        Name of the operator: {'maximum', 'probsum'}
        """
        if name == 'maximum':
            return cls(cls.maximum).get
        elif name == 'probsum':
            return cls(cls.probsum).get
        else:
            raise NotImplementedError



class TriangularSet:
    """Triangular fuzzy set.
    
    Attributes:
        left
        leftBorder
        right
        rightBorder
        orientation
    """
    def __init__(self, width=1, xcenter=0, infiniteSide=None):
        """Constructor of TriangularSet.
        
        Arguments:
            width
            xcenter
            infiniteSide
        """
        # conditions
        assert(width > 0)
        assert( infiniteSide in {"L","R",None} )
        # creating inner properties
        self.left = lambda x : (x-xcenter)/width + 1
        self.leftBorder = (xcenter-width, xcenter)
        self.right = lambda x : -(x-xcenter)/width + 1
        self.rightBorder = (xcenter, xcenter+width)
        self.orientation = infiniteSide
            
    def getLeftInfinite(self, x):
        """Returns value from left side, if infinite.
        
        Arguments:
            x
        """
        if x >= self.rightBorder[1]:
            return 0
        elif x >= self.rightBorder[0]:
            return self.right(x)
        else:
            return 1
    def getRightInfinite(self, x):
        """Returns value from right side, if infinite.
        
        Arguments:
            x
        """
        if x <= self.leftBorder[0]:
            return 0
        elif x <= self.leftBorder[1]:
            return self.left(x)
        else:
            return 1
    def getTriangle(self, x):
        """Returns value from not inifinite set.
        
        Arguments:
            x
        """
        if x >= self.leftBorder[0] and x <= self.leftBorder[1]:
            return self.left(x)
        elif x >= self.rightBorder[0] and x <= self.rightBorder[1]:
            return self.right(x)
        else:
            return 0

    def get(self, x):
        """Returns value from general set.
        
        Arguments:
            x
        """
        if self.orientation == "L":
            return self.getLeftInfinite(x)
        elif self.orientation == "R":
            return self.getRightInfinite(x)
        else:
            return self.getTriangle(x) 


class ArctangenoidSet:
    """Arctangenoid fuzzy set.
    
    Attributes:
        get         Membership function
    """
    def __init__(self, width=1, xcenter=0, side="L"):
        """Constructor of ArctangenoidSet.
        
        Arguments:
            width       Variance of the arctangenoid.
            xcenter     Center of the arctangenoid.
            side        Orientation {'L','R'} of '1' part.
        """
        # premises
        assert(width > 0)
        assert( side in {"L","R"} )
        # orientation
        if side == 'L':
            self.get = lambda x : math.atan( 4*(-x-xcenter-width)/width ) / math.pi + 0.5
        elif side == 'R':
            self.get = lambda x : math.atan( 4*(x-xcenter-width)/width ) / math.pi + 0.5

class GaussianSet:
    """Gaussian fuzzy set.
    
    Attributes:
        get         Membership function.
    """
    def __init__(self, width=1, xcenter=0):
        """Construcotr of GaussianSet.
        
        Arguments:
            width       Variance of the gaussian.
            xcenter     Centr of the gaussian.
        """
        # premises
        assert(width > 0)
        # substitution
        mu = xcenter
        var = width
        # formula
        self.get = lambda x : math.sqrt(math.exp(-((mu-x)**2)/(2*(0.6*var)**2)))





# called directly
if __name__ == '__main__':
    from globals import *
    raise NotCallableModuleError
    