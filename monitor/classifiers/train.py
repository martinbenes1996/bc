
import sys

sys.path.insert(0, '.')
import conf
import model

class Trainer:
    def __init__(self, trainset = None):
        if trainset != None:
            model.Classification.setTrainSet(trainset, persistent=True)
        self.classification = model.Classification.retrain()

def main():
    if len(sys.argv) > 1:
        trainer = Trainer(sys.argv[1:])
    else:
        trainer = Trainer()




if __name__ == '__main__':
    main()
