
import math
import tkinter as tk


class App(tk.Canvas):
    """View of the client and window at once. Singleton.
    
    Attributes:
        app_    Main app to call mainloop() on.
    """
    app_ = None # app instance
    def __init__(self, master=None):
        """Constructor.
        
        Keyword arguments:
            master      Master of app. None defaultly.
        """
        # instatiate window
        self.winsize = {'height': 1000, 'width': 1000}
        super().__init__(master, bg="#267158",
            width=self.winsize['width'], height=self.winsize['height'])
        # save attribute inside
        self.master = master
        self.sensors = []
        # fill and display window
        self.create_window()
        self.pack()
    
    @classmethod
    def get(cls):
        """Instance getter."""
        # instantiate if not instanced yet
        if cls.app_ == None:
            cls.app_ = cls(master=tk.Tk())

        return cls.app_
    
    def create_window(self):
        """Creates window content."""
        # displays modul symbol with given parameters
        self.add_modul(x=500,y=500,omega=60, side=150)
    
    def add_modul(self, x, y, omega, side=100, azimuth=0):
        """Creates and displays modul symbol with given parameters.
        
        Keyword arguments:
            x           x-coordinate of middle sensor
            y           y-coordinate of middle sensor
            omega       angle between sensors axis
            side        size of side
            azimuth     orientation of whole modul
        """
        # middle
        self.add_sensor(x, y, 0, "#0e553e")
        
        # side
        d = side/2.
        dx = d + math.cos(math.radians(omega))*d
        dy = math.sin(math.radians(omega))*d
        self.add_sensor(x-dx, y+dy, omega + azimuth, "#0d453a")

        # side
        self.add_sensor(x+dx, y+dy, -omega + azimuth, "#0d453a")

    def add_sensor(self, x, y, azimuth, color):
        """Creates and displays sensor within module with given parameters.
        
        Keyword arguments:
            x           x-coordinate of sensor
            y           y-coordinate of sensor
            azimuth     azimuth of sensor
            color       color of arc background
        """
        # draw arc
        radius = {'x': self.winsize['width']/3., 'y': self.winsize['height']/3.}
        coords = x-radius['x'], y-radius['y'], x+radius['x'], y+radius['y']
        arc = self.create_arc(coords, start=azimuth+90-50, extent=100, fill=color, outline="", stipple="gray50")
        # draw line
        endx = x + math.cos(math.radians(azimuth+90))*radius['x']
        endy = y + math.sin(math.radians(azimuth-90))*radius['y']
        line = self.create_line(x, y, endx, endy, fill="black", dash=(4,4))
        # save sensor
        self.sensors.append( {'arc': arc,'line': line} )