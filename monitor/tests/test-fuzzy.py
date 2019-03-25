
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
    test(s4.get(0), 0)
    test(s4.get(1), 0)
    test(s4.get(-10), 0.5)
    test(s4.get(-100), 1, 0.01)

    s5 = fuzzy.ArctangenoidSet(10, side="R")
    test(s5.get(0), 0)
    test(s5.get(10), 0.5)
    test(s5.get(-1), 0)
    test(s5.get(100), 1, 0.01)

def testKhi():
    toleranceStagnation = segment.Edge.toleranceStagnation
    Khi = segment.Edge.Khi

    test(Khi["S"](0), 1)
    test(Khi["F"](0), 0)
    test(Khi["R"](0), 0)

    test(Khi["S"](-50), 0)
    test(Khi["S"](50), 0)
    test(Khi["S"](toleranceStagnation), 0.5, 0.01)
    test(Khi["S"](-toleranceStagnation), 0.5, 0.01)

    test(Khi["F"](10), 0)
    test(Khi["F"](-toleranceStagnation), 0.5, 0.01)
    test(Khi["F"](-100), 1, 0.01)

    test(Khi["R"](-10), 0)
    test(Khi["R"](toleranceStagnation), 0.5, 0.01)
    test(Khi["R"](100), 1, 0.01)

def main():
    testSet()
    testKhi()

    assert(status)


if __name__ == "__main__":
    main()