
import sys

sys.path.insert(0, '.')
import fuzzy



def testSet():
    s1 = fuzzy.TriangularSet(1)
    assert(s1.get(0) == 1)
    assert(s1.get(1) == 0)
    assert(s1.get(2) == 0)
    assert(s1.get(-1) == 0)
    assert(s1.get(0.5) - 0.5 < 0.0001) # s1.get(0.5) == 0.5
    assert(s1.get(-0.9) - 0.1 < 0.0001) # s1.get(-0.9) == 0.1

    s2 = fuzzy.TriangularSet(5, 2)
    assert(s2.get(2) == 1)
    assert(s2.get(7) == 0)
    assert(s2.get(-3) == 0)
    assert(s2.get(-0.5) - 0.5 < 0.0001) # s2.get(-0.5) == 0.5
    assert(s2.get(6) - 0.2 < 0.0001) # s2.get(6) == 0.2

    s3 = fuzzy.TriangularSet(0.5, -0.5, "L")
    assert(s3.get(0) == 0)
    assert(s3.get(1) == 0)
    assert(s3.get(-1) == 1)
    assert(s3.get(0.001) == 0)
    assert(s3.get(0.25) - 0.25 < 0.0001) # s3.get(0.25) == 0.25

def main():
    testSet()


if __name__ == "__main__":
    main()