
import numpy as np
import sys

sys.path.insert(0, '.')
import model


class Evaluator:

    def sigmoid(self,kappa):
        #if kappa >= 0.5:
        #    return 1
        #else:
        #    return 0
        return kappa

    def evaluate(self, key):
        # train
        c = model.Classification.getTrained()
        # test
        results,sizes = c.evaluate()
        assert(len(results) == len(sizes))
        # used in loops
        resultscore,positivescore,negativescore = 0,0,0 # scores
        totalN,ptotalN,ntotalN = 0,0,0                  # lengths

        # iterate over tests
        for testname,result in results.items():
            # artefact sizes vector
            artefactsSizes = sizes[testname][0]
            assert(len(result) == len(artefactsSizes))
            # summing sizes up
            sampleN = sum(artefactsSizes)
            psampleN = sum([s for i,s in enumerate(artefactsSizes) if result[i][key][1] == True])
            nsampleN = sum([s for i,s in enumerate(artefactsSizes) if result[i][key][1] == False])
            # adding to totals
            totalN += sampleN
            ptotalN += psampleN
            ntotalN += nsampleN

            # used in loop
            positives,negatives,testResult = [],[],[]
            # loop over artefacts
            for i,res in enumerate(result):
                # weight
                aW = artefactsSizes[i]
                # score and key (kappa)
                score,kappa = res[key][0],res[key][1]
                # N
                if kappa == None:
                    print("None!")
                    continue
                # 1
                elif kappa == True:
                    weightedScore = self.sigmoid(score) * aW
                    resultscore += weightedScore
                    positivescore += weightedScore
                # 0
                elif kappa == False:
                    weightedScore = self.sigmoid(1-score) * aW
                    resultscore += weightedScore
                    negativescore += weightedScore

        # normalizing, converting to percents
        positivescore *= 100 / ptotalN
        negativescore *= 100 / ntotalN
        resultscore *= 100 / totalN
        # logging
        print("Positive score: ", positivescore)
        print("Negative score: ", negativescore)
        print("=======================")
        print("Result score:", resultscore)

        return (positivescore,negativescore)

    def optimize(self, key):

        # train
        c = model.Classification.getTrained()
        # test
        results,sizes = c.evaluate()
        assert(len(results) == len(sizes))
        # used in loops
        resultscore,positivescore,negativescore = 0,0,0 # scores
        totalN,ptotalN,ntotalN = 0,0,0                  # lengths
        
        # optimize
        for ki in (-0.1,-0.05,-0.01,-0.005,-0.001):
            for kj in (-0.1,-0.05,-0.01,-0.005,-0.001):
                model.LinearRegression.smoothenSlopeForwards = ki
                model.LinearRegression.smoothenSlopeBackwards = kj
                pscore,nscore = self.evaluate(key)
                print(ki,kj,">",pscore,nscore)




def main():
    e = Evaluator()
    e.evaluate('presence')
   
    


if __name__ == '__main__':
    main()