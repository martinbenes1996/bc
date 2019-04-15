
import numpy as np
import sys

sys.path.insert(0, '.')
import model


class Evaluator:

    def evaluate(self, key):
        # train
        c = model.Classification.getTrained()
        # test
        results = c.test()
        positives,negatives = [],[]
        for testname,result in results.items():
            scores = [i[key][0] for i in result]
            N = len(scores)

            for i in result:
                score = i[key][0]
                if i[key][1]:
                    positives.append(score)
                else:
                    negatives.append(score)
            
        pscore = np.mean(positives)*100
        nscore = np.mean(negatives)*100

        print("Positive score:", pscore)
        print("Negative score:", nscore)

        totalscore = (pscore*len(positives) + nscore*len(negatives) ) / N
        print("Total score:", totalscore)

def main():
    e = Evaluator()
    e.evaluate('presence')
   
    


if __name__ == '__main__':
    main()
