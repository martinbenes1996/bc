
import json
import sys

TRAINTEST_RATIO = (2/3)

def split(labelfile):
    with open('../data/'+labelfile+'/label.json') as f:
        # parse data and filenames
        data = json.load(f)
        files = sorted(list(data.keys()))
        # count traintest ratio
        traincnt = int(len(files) * TRAINTEST_RATIO)
        # create filenames
        trainfiles = files[:traincnt]
        testfiles = files[traincnt:]
        # create data dicts
        traindata = dict((k,data[k]) for k in trainfiles)
        testdata = dict((k,data[k]) for k in testfiles)
        # output
        with open('../data/'+labelfile+'/train.json','w') as t:
            json.dump(traindata,t)
        with open('../data/'+labelfile+'/test.json','w') as t:
            json.dump(testdata,t)


if __name__ == '__main__':
    assert(len(sys.argv) == 2)
    split(sys.argv[1])