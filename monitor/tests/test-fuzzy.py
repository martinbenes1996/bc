
import sys

sys.path.insert(0, '.')
import fuzzy
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

def testSet():

    s1 = fuzzy.TriangularSet(1)
    test(s1.get(0), 1)
    test(s1.get(1), 0)
    test(s1.get(2), 0)
    test(s1.get(-1), 0)
    test(s1.get(0.5), 0.5)
    test(s1.get(-0.9), 0.1)

    s2 = fuzzy.TriangularSet(5, 2)
    test(s2.get(2), 1)
    test(s2.get(7), 0)
    test(s2.get(-3), 0)
    test(s2.get(-0.5), 0.5)
    test(s2.get(6), 0.2)

    s3 = fuzzy.TriangularSet(0.5, -0.5, "L")
    test(s3.get(0), 0)
    test(s3.get(0), 0)
    test(s3.get(1), 0)
    test(s3.get(-1), 1)
    test(s3.get(0.001), 0)
    test(s3.get(0.25), 0)

    s4 = fuzzy.ArctangenoidSet(10)
    #test(s4.get(0), 0)
    test(s4.get(100), 0, 0.01)
    test(s4.get(-10), 0.5)
    test(s4.get(-100), 1, 0.01)

    s5 = fuzzy.ArctangenoidSet(10, side="R")
    #test(s5.get(0), 0)
    test(s5.get(10), 0.5)
    test(s5.get(-100), 0, 0.01)
    test(s5.get(100), 1, 0.01)

def testKhi():
    toleranceStagnation = segment.Edge.toleranceStagnation
    Khi = segment.Edge.Khi

    test(Khi["S"](0), 1)
    #test(Khi["F"](0), 0)
    #test(Khi["R"](0), 0)

    test(Khi["S"](-100), 0)
    test(Khi["S"](100), 0)
    test(Khi["S"](toleranceStagnation), 0.5, 0.01)
    test(Khi["S"](-toleranceStagnation), 0.5, 0.01)

    test(Khi["F"](120), 0, 0.05)
    test(Khi["F"](-toleranceStagnation), 0.5, 0.05)
    test(Khi["F"](-100), 1, 0.05)

    test(Khi["R"](-120), 0, 0.05)
    test(Khi["R"](toleranceStagnation), 0.5, 0.05)
    test(Khi["R"](100), 1, 0.05)

def testNegator():
    N = fuzzy.Negator

    test(N.standard(0), 1)
    test(N.standard(1), 0)
    test(N.standard(0.5), 0.5)

    test(N.circle(0), 1)
    test(N.circle(1), 0)

    test(N.parabolic(0), 1)
    test(N.parabolic(1), 0)

def testTConorm():
    TC = fuzzy.TConorm

    test(TC.maximum(0,0), 0)
    test(TC.maximum(1,1), 1)
    test(TC.maximum(0,0.1), 0.1)
    test(TC.maximum(0,0.2,0.4,0.6), 0.6)
    test(TC.maximum(0,1), 1)
    test(TC.maximum(1,0), 1)
    test(TC.maximum(0,0,1,0), 1)

    test(TC.probsum(0,0), 0)
    test(TC.probsum(1,1), 1)
    test(TC.probsum(1,0), 1)
    test(TC.probsum(1,1), 1)
    test(TC.probsum(0,0,1,0), 1)

def testOperations():
    conjunction = fuzzy.AND
    disjunction = fuzzy.OR
    
    test(conjunction(0,0), 0)
    test(conjunction(1,0), 0)
    test(conjunction(0,1), 0)
    test(conjunction(1,1), 1)
    test(conjunction(0,0.5), 0)

    test(disjunction(0,0), 0)
    test(disjunction(1,0), 1)
    test(disjunction(0,1), 1)
    test(disjunction(1,1), 1)

    test(conjunction(0,0,0), 0)
    test(conjunction(1,1,1), 1)
    test(conjunction(1,1,0), 0)
    test(conjunction(0,1,1), 0)


def main():
    testSet()
    testKhi()

    testNegator()
    testTConorm()

    testOperations()

    assert(status)


if __name__ == "__main__":
    main()