
import os
import sys

sys.path.insert(0, '.')
import comm_replay
import conf
import segment

class InvalidInput(Exception):
    def __init__(self, i):
        super().__init__("Invalid input \""+i+"\"")
class InvalidTraining(Exception):
    def __init__(self, msg):
        super().__init__(msg)

class Labeller:
    def __init__(self):
        print("Current directory is \""+os.getcwd()+"\".")

    def label(self, path):
        # check whether exists
        if os.path.exists(path) and os.path.isdir(path):
            # get exercises
            exercises = Exercise.get(path)
            # label each exercise
            for e in exercises:
                e.label()

        else:
            raise InvalidTraining('Invalid train directory \"'+path+'\"')

class Exercise:
    @classmethod
    def get(cls, path):
        exerciseName = os.path.basename(path)
        exercises = []
        i = 1
        while True:
            # parse file names
            name = path + '/' + exerciseName + '_' + str(i)
            datafile,videofile,labelfile = name+'.csv', name+'.mov', name+'.json'

            try:
                # check if exists
                if not os.path.isfile(datafile):
                    raise InvalidTraining(datafile + ' does not exist.')
                # uncomment, when video processed
                #if not os.path.isfile(videofile):
                #    raise InvalidTraining(videofile + ' does not exist.')
            except:
                break

            # add
            exercises.append( cls(datafile, videofile, labelfile) )
            i += 1
        return exercises


    def __init__(self, datafile,videofile,labelfile):
        # check if exists
        if not os.path.isfile(datafile):
            raise InvalidTraining(datafile + ' does not exist.')
        # uncomment, when video processed
        #if not os.path.isfile(videofile):
        #   raise InvalidTraining(videofile + ' does not exist.')

        # files
        self.datafile = datafile
        self.videofile = videofile

        

    def label(self):
        timestamps = []
        
        # process data
        x = comm_replay.Reader.readFile(self.datafile)
        artefacts = segment.Artefact.parseArtefacts(x)
        # process video
        fps = 25 # TODO

        # comparing
        pos = 0
        for i,a in enumerate(artefacts):
            print('Process artefact '+str(i+1) + ' of '+self.datafile)
            l = a.len()

            # counting a center time of artefact
            fs = conf.Config.fs()
            t = (pos + l/2) / fs

            # getting the video frame
            frameIndex = t * fps
            # frame = video[frameIndex] # TODO
            # frame.show()
            
            # ask user with input for true/false position # TODO

            # add result to list timestamps[]

            # moving starting position to next artefact
            pos += l
        
        return timestamps
        
    @classmethod
    def parseBool(cls, s):
        if s.lower() in {'true', 't', 'yes', 'yeah', 'yea', 'ano', 'jo', 'ja', '1', 'right', 'richtig', 'recht'}:
            return True
        elif s.lower() in {'false', 'f', 'no', 'nein', 'nah', 'ne', '0', 'falsch'}:
            return False
        else:
            raise InvalidInput(s)





def main():
    l = Labeller()

    while True:
        try:
            path = input('Label >> ')
        except EOFError:
            print('')
            break
        try:
            l.label(path)
        except (InvalidInput,InvalidTraining) as e:
            print(e)


if __name__ == "__main__":
    main()

