# Bio

Project focusing on classification of situation (count of people etc.) using PIR sensors. Done as bachelor thesis
of Martin Benes, student of Faculty of Information Technologies, Brno University of Technology.

# Structure of the project #

## data ##
Data contains data, recorded from the sensors. There is multiple cathegories of data

* c - circular
* d - diagonal
* e - empty
* o - older recording
    * oE - empty
    * o[0-9] - circular

Each recording has its own directory. The session includes 3 15s recordings (_1,_2,_3). The recording is saved
in csv format, recording also contains mp4 format. Each session is labeled, the label is stored in 
file label.json in every session directory.

Except of that to operate the data, the visualizing program *show.py* is included. Its usage is

*$ python3 show.py <session>/<session>_<recordingNum>.json*
 
## monitor ##
Monitor is the classification server, that collects data from the sensors and processes the samples using
feature extraction and classification into fuzzy map of presence of objects. It has GUI for purposes of
visualization. The input signal can be read from following sources.

* serial line
* multicast channel
* file



## module ##
Module contains everything around hardware and module. Not only programs, that are loaded in the MCU's,
also configuration for collector etc.
