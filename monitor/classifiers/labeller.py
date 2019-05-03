
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
            labelfilename = path+'/label.json'
            with open(labelfilename, 'w') as labelfile:
                json.dump(labels, labelfile)
            print("Label written to", labelfilename+'.')

        else:
            raise InvalidTraining('Invalid train directory \"'+path+'\"')
    
    def check(self, name, key):
        path = '../data/'+name
        # check whether exists
        if os.path.exists(path) and os.path.isdir(path):
            # get exercises
            exercises = Exercise.get(name)
            # check each exercise
            for e in exercises:
                e.check(key)
        else:
            raise InvalidTraining('Invalid train directory \"'+path+'\"')

class VideoFile:
    def __init__(self, path):
        self.show = True
        self.video = cv2.VideoCapture(path)
        if not self.video.isOpened():
            self.show = False
        self.fps = self.video.get(cv2.CAP_PROP_FPS)
        self.maxFrames = self.video.get(cv2.CAP_PROP_FRAME_COUNT)
    def showFrame(self, time):
        frameIndex = int(time*self.fps)
        self.video.set(1,frameIndex)
        ret,frame = self.video.read()
        self.windowname = 'Frame '+str(frameIndex)
        cv2.imshow(self.windowname, frame)
    def waitKey(self):
        while True:
            keyCode = cv2.waitKey(100)
            if keyCode != -1:
                return keyCode
    def getValue(self, question):
        print(question, end='')
        sys.stdout.flush()
        try:
            while cv2.getWindowProperty(self.windowname, 0) >= 0:
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


class Exercise:
    @classmethod
    def get(cls, name):
        exercises = []
        i = 1
        while True:
            # parse file names
            labelfile = '../data/'+name+'/label.json'
            path = '../data/' + name+ '/' + name + '_' + str(i)
            datafile,videofile = path+'.csv', path+'.mp4'
            

            try:
                # check if exists
                if not os.path.isfile(datafile):
                    raise InvalidTraining(datafile + ' does not exist.')
                # uncomment, when video processed
                #if not os.path.isfile(videofile):
                #    raise InvalidTraining(videofile + ' does not exist.')
            except InvalidTraining as e:
                #print(e)
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
        self.labelfile = labelfile
        

    def label(self):
        timestamps = []
        fs = conf.Config.fs()
        # process data
        x = comm_replay.Reader.readFile(self.datafile)
        artefacts = segment.Artefact.parseArtefacts(x)
        # process video
        video = VideoFile(self.videofile)

        # comparing
        pos = 0
        for i,a in enumerate(artefacts):
            # counting a center time of artefact
            l = a.len()
            t = (pos + l/2) / fs

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
                video.showFrame(t)
                # ask
                presentKey = video.getValue('Is the person present? ')
                if not presentKey:
                    keys = (False, None, None, None)
                else:
                    keys = (presentKey,
                            video.getValue('\tIs the person close the center? '), 
                            video.getValue('\tIs the person on the left? '),
                            video.getValue('\tIs the person close? ') )
            except cv2.error:
                keys = (False,None,None,None)

            result = {'key':keys, 'start': pos, 'length': l}
            timestamps.append(result)

            # moving starting position to next artefact
            pos += l
        return timestamps
        
    def check(self, key):
        def printQuestion(question,answer):
            print(question,end=' ')
            if answer is True:
                print('Yes.')
            elif answer is False:
                print('No.')
            elif answer is None:
                print('Unknown.')
            else:
                raise InvalidTraining("Unknown answer: "+str(answer))
        print('========================')
        print('Checking ',self.labelfile)
        fs = conf.Config.fs()
        labels = json.load(open(self.labelfile,'r'))
        video = VideoFile(self.videofile)
        artefacts = labels[self.name]

        for a in artefacts:
            t = (a['start'] + a['length']/2) / fs
            video.showFrame(t)
            # print label
            if a['key'][0] is False:
                printQuestion('Is the person present?', a['key'][0])
            else:
                for i,q in enumerate(('Is the person present?','\tIs the person close the center?','\tIs the person on the left?','\tIs the person close?')):
                    printQuestion(q,a['key'][i])
            video.waitKey()
            
            



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
            if path.split(' ')[0] == 'check':
                l.check(path.split(' ')[1], 'center')
            else:
                l.label(path)
        except (InvalidInput,InvalidTraining) as e:
            print(e)


if __name__ == "__main__":
    main()

