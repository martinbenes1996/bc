
import conf
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure

class Viewer:

    def __init__(self, inline=False):
        self.inline = inline
        self.cwt_widths = np.arange(1,31)
        if inline:
            self.cwt_fig = Figure(figsize=(6,4), dpi=100)
        else:
            self.cwt_fig = plt.figure()
        self.cwt_ax = self.cwt_fig.add_subplot(111)
        self.cwt_ax.set_xlabel("Samples")
        self.cwt_ax.set_ylabel("CWT Coeffs")
        coefs = conf.Config.cwtCoefs()
        self.cwt_ax.set_ylim(coefs[0],coefs[-1])
        self.cwt_cb = None
        N,overlap = conf.Config.segment()
        self.cwt_x, self.cwt_y = np.meshgrid(np.arange(0,N), np.logspace(np.log10(coefs[-1]), np.log10(coefs[0]), np.size(coefs)))

    def cwt(self, X):
        c = self.cwt_ax.pcolormesh(self.cwt_x, self.cwt_y, X, cmap='PRGn', vmin=-100, vmax=100)
        if self.cwt_cb != None:
            self.cwt_cb.remove()
        self.cwt_cb = self.cwt_fig.colorbar(c)
        if not self.inline:
            plt.pause(10e-9)