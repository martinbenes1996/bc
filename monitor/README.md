# Bio #

Monitor is the classification server, that collects data from the sensors and performs
classification algorithms over them. The input signal can be read from following sources.

* serial line
* multicast channel
* file

## Installation ##

Reading the serial file in Linux requires superuser privilegies, or membership in group *dialout*.
Recommended is the second option. To join it, following command must be ran and then computer restarted.

*$ sudo usermod -a -G dialout $USER*

## Running ##

The required libraries are listed in file *requirements.txt*, install them using

*$ pip install -r requirements.txt*

Alternatively, a running environment with all the needed dependecies is present.
It can be activated with

*$ source env/bin/activate*

After that, the program can be launched.

*$ python3 main.py*

Leaving the environment is done by *deactivate* command.

