
import json
import os
import sys
import _thread
import time

import cv2
import matplotlib.pyplot as plt
import numpy as np

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
class ExitException(Exception):
    pass

class Labeller:
    def __init__(self):
        print("Current directory is \""+os.getcwd()+"\".")

    def label(self, name):
        path = '../data/'+name
        # check whether exists
        if os.path.exists(path) and os.path.isdir(path):
            # get exercises
            exercises = Exercise.get(name)
            # label each exercise
            labels = {}
            for e in exercises:
                try:
                    labels[e.name] = e.label()
                except ExitException:
                    continue
            labelfilename = path+'/'+'label.json'
            with open(labelfilename, 'w') as labelfile:
                json.dump(labels, labelfile)
            print("Label written to", labelfilename+'.')

        else:
            raise InvalidTraining('Invalid train directory \"'+path+'\"')

class Exercise:
    @classmethod
    def get(cls, name):
        exercises = []
        i = 1
        while True:
            # parse file names
            path = '../data/' + name+ '/' + name + '_' + str(i)
            datafile,videofile,labelfile = path+'.csv', path+'.mp4', path+'.json'
            

            try:
                # check if exists
                if not os.path.isfile(datafile):
                    raise InvalidTraining(datafile + ' does not exist.')
                # uncomment, when video processed
                #if not os.path.isfile(videofile):
                #    raise InvalidTraining(videofile + ' does not exist.')
            except InvalidTraining as e:
                print(e)
                break
            except Exception as e:
                print(e)
                break

            # add
            exercises.append( cls(name+'_'+str(i), datafile, videofile, labelfile) )
            i += 1
        return exercises


    def __init__(self, name, datafile,videofile,labelfile):
        self.name = name
        # check if exists
        if not os.path.isfile(datafile):
            raise InvalidTraining("Data file " + datafile + ' does not exist.')
        # uncomment, when video processed
        #if not os.path.isfile(videofile):
        #   raise InvalidTraining("Video file " + videofile + ' does not exist.')

        # files
        self.datafile = datafile
        self.videofile = videofile

        

    def label(self):
        timestamps = []
        # sampling frequency
        fs = conf.Config.fs()
        #print("Signal sampling frequency:", fs)
        
        # process data
        x = comm_replay.Reader.readFile(self.datafile)
        artefacts = segment.Artefact.parseArtefacts(x)
        # process video
        showVideo = True
        video = cv2.VideoCapture(self.videofile)
        if not video.isOpened():
            showVideo = False
            #raise InvalidTraining(self.videofile + ' can not be read.')
        fps = video.get(cv2.CAP_PROP_FPS)
        maxFrames = video.get(cv2.CAP_PROP_FRAME_COUNT)

        #print("Read video", self.videofile+".", str(fps), "FPS,",str(maxFrames),"frames", str(maxFrames/fps),"s")
        print("Labeling", self.videofile)
        # comparing
        pos = 0
        for i,a in enumerate(artefacts):
            l = a.len()

            # counting a center time of artefact
            t = (pos + l/2) / fs

            # getting the video frame
            frameIndex = int(t * fps)
            #print('Artefact '+str(i+1) + ':', (l/fs), 's /', (l/fs)*fps, 'frames, represented by', frameIndex)

            try:
                # plot graph
                y = a.samples()
                x = np.linspace(0,len(y),len(y))
                plt.clf()
                plt.plot(x,y,c='r')
                axes = plt.gca()
                axes.set_ylim([0,1023])
                plt.pause(0.01)
                # show video
                video.set(1,frameIndex)
                ret,frame = video.read()

                windowname = 'Frame '+str(frameIndex)
                cv2.imshow(windowname, frame)
            
                presentKey = self.getValue('Is the person present? ', windowname)
                if not presentKey:
                    keys = (False, None, None, None)
                else:
                    keys = (presentKey,
                            self.getValue('\tIs the person close the center? ', windowname), 
                            self.getValue('\tIs the person on the left? ', windowname),
                            self.getValue('\tIs the person close? ', windowname) )
                #cv2.destroyWindow(windowname)
            except cv2.error:
                keys = (False,None,None,None)


            result = {'key':keys, 'start': pos, 'length': l}

            timestamps.append(result)

            # moving starting position to next artefact
            pos += l
        
        return timestamps
    
    def getValue(self, question, windowname):
        print(question, end='')
        sys.stdout.flush()
        try:
            while cv2.getWindowProperty(windowname, 0) >= 0:
                keyCode = cv2.waitKey(100)
                if keyCode in {177, 121, 89}:
                    print("Yes.")
                    return True
                elif keyCode in {176,110,78}:
                    print("No.")
                    return False
                elif keyCode in {27}:
                    print("Exit.")
                    cv2.destroyAllWindows()
                    raise ExitException
        except cv2.error:
            print("Exit.")
            raise ExitException

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
        except KeyboardInterrupt:
            print('Exit')
            return
        try:
            l.label(path)
        except (InvalidInput,InvalidTraining) as e:
            print(e)


if __name__ == "__main__":
    main()

