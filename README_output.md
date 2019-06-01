# Bio

Project focusing on classification of situation (count of people etc.) using PIR sensors. Done as bachelor thesis
of Martin Benes, student of Faculty of Information Technologies, Brno University of Technology.

# Setup #
If you have the compressed file xbenes49.tar.gz, first you need to decompress, extract and enter the project with:

*$ tar -xf xbenes49.tar.gz && cd xbenes49 *


# Structure of the project #

The directory contains following structure:

* data/
* monitor/
* module/

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


# Main procedures #
## Activate the environment ##
To enter the prepared virtual environment, type down following commands:

*$ cd monitor/ *
*$ source env/bin/activate *

# Run #

To start the classification server, execute inside of the virtual environment one of following commands:

*$ python3 main.py*
*$ make run * 

# Manual training of classifier #
To retrain the classifier, execute inside of the virtual environment one of the following commands:

*$ python3 classifiers/train.py *
*$ make train *

The used data for training are saved in the .json format in the file *classifiers/trainset.json*.

# Evaluation of score #
To evaluate the classifier on testing data, execute inside of the virtual environment one of the following commands:

*$ python3 classifiers/evaluator.py *
*$ make evaluate *

The displayed trait can be altered inside of the code in the function *main()* in the module *evaluator.py*.

# Label data #
Data can be labeled inside of the virtual environment by one of the following commands:

*$ python3 classifiers/labeller.py *
*$ make label *

The input must be session name to create new label for session (e.g. c5m_RL_1).
It is also possible to check existing label, with input starting with "check" (e.g. check c5_RL_1).
