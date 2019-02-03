#!/usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt
import sys

M = []
for n in range(1,100):
    try:
        a = np.genfromtxt(sys.argv[2]+"_segment"+str(n)+"_cwt.csv", delimiter=',')
    except IOError as e:
        break
    M.append(a)

print("Loaded", len(M), "files.")

for m in M:
    print(m)
    plt.imshow(m, cmap='PRGn', aspect='auto', vmax=m.max(), vmin=m.min())
    plt.pause(1)