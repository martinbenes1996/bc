
import sys

sys.path.insert(0, '.')
import conf
import model


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
def my_assert(cond):
    global status
    global i
    i += 1
    if not cond:
        if status:
            print("")
        print(str(i)+": False", file=sys.stderr)
        status = False


def main():
    conf.Config.setDebug(False)
    trains,tests = model.Reference.generateReferences("c4m_LR_3", traintest=True)

    test(trains["c4m_LR_3_1"].artefactOfSample(153), 1)
    test(trains["c4m_LR_3_1"].artefactOfSample(190), 1)
    test(trains["c4m_LR_3_1"].artefactOfSample(205), 1)
    test(trains["c4m_LR_3_1"].artefactOfSample(206), 2)

    test(trains["c4m_LR_3_1"].getRangeReference(573,625)["presence"], 0.5)
    


    assert(status)



if __name__ == "__main__":
    main()