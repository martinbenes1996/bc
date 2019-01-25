# bc

Bachelor thesis of Martin Benes.

# Structure of the project #

## collector ##
Collector collects data from sensors and processes the samples using feature extraction and classification into
fuzzy map of presence of objects.

In different thread it performs fusion of the data from multiple sensors into one map and sends to a multicast.
The visualization is done by visualizer.

The collector uses library *json* by *nlohmann* (https://github.com/nlohmann/json) to cooperate with json config file.

## data ##
Data contains data, recorded from the sensors. Except of that there are also following python programs.

* replay.py - replays the records for the collector as it was sent by a sensor
* show.py - visualizes samples in a graph
* record.py - saves the records from the sensors into file

## module ##
Module contains everything around hardware and module. Not only programs, that are loaded in the MCU's,
also configuration for collector etc.

## other ##
Other files. Presentations, links etc.

## sources ##
Important sources for the thesis.

## text ##
The thesis latex project with bibtex and Makefile to compile.

## visualizer ##
Python program, that listens to a multicast channel and visualizes output of collector.

