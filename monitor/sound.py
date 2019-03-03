#!/usr/bin/env python

#"""Play a fixed frequency sound."""
#from __future__ import division
#import math

#from pyaudio import PyAudio # sudo apt-get install python{,3}-pyaudio

#try:
#    from itertools import izip
#except ImportError: # Python 3
#    izip = zip
#    xrange = range

#def sine_tone(frequency, duration, volume=1, sample_rate=22050):
#    n_samples = int(sample_rate * duration)
#    restframes = n_samples % sample_rate

#    p = PyAudio()
#    chosen_device_index = -1
#    for x in xrange(0,p.get_device_count()):
#        info = p.get_device_info_by_index(x)
#        print(p.get_device_info_by_index(x))
#        if info["name"] == "pulse":
#            chosen_device_index = info["index"]
#            print("Chosen index: ", chosen_device_index)
#            break
#    
#    stream = p.open(format=p.get_format_from_width(1), # 8bit
#                    channels=1, # mono
#                    output_device_index=chosen_device_index,
#                    rate=sample_rate,
#                    output=True)
#    s = lambda t: volume * math.sin(2 * math.pi * frequency * t / sample_rate)
#    samples = (int(s(t) * 0x7f + 0x80) for t in xrange(n_samples))
#    for buf in izip(*[samples]*sample_rate): # write several samples at a time
#        stream.write(bytes(bytearray(buf)))
#
#    # fill remainder of frameset with silence
#    stream.write(b'\x80' * restframes)
#
#    stream.stop_stream()
#    stream.close()
#    p.terminate()

import os
def sine_tone(frequency, duration, volume=1, sample_rate=22050):
    os.system("pwd")
    os.system("echo $USER")
    os.system("./beep.sh "+str(frequency)+" "+str(duration))
