
import math
import tkinter as tk
import time


class App(tk.Canvas):
    """View of the client and window at once. Singleton.
    
    Attributes:
        app_    Main app to call mainloop() on.
    """
    app_ = None # app instance
    def __init__(self, master=None):
        """Constructor.
        
        Keyword arguments:
            getdata     Callback function to get data.
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
        # save callback
        self.getData = lambda : []
        # create drawn objects
        self.objects = []
        # run timer for painting
        self.update()

    
    @classmethod
    def get(cls):
        """Instance getter."""
        # instantiate if not instanced yet
        if cls.app_ == None:
            cls.app_ = cls(master=tk.Tk())

        return cls.app_
    
    def polar2global(self, azimuth, distance):
        x,y = self.winsize['width']/2., self.winsize['height']/2.
        return x + math.cos(math.radians(azimuth+90))*distance, y + math.sin(math.radians(azimuth-90))*distance 

    
    def create_window(self):
        """Creates window content."""
        # displays modul symbol with given parameters
        centerx, centery = self.winsize['width']/2., self.winsize['height']/2.
        self.add_modul(x=centerx, y=centerx, omega=60, side=150, azimuth=0)
    
        
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
        self.add_sensor(x, y, azimuth, "#0e553e")

        # side
        d = side/2.
        dx = d + math.cos(math.radians(omega))*d
        dy = math.sin(math.radians(omega))*d
        self.add_sensor(x-math.cos(math.radians(azimuth))*dx, y+math.sin(math.radians(azimuth))*dy, omega+azimuth, "#0d453a")

        # side
        self.add_sensor(x+math.cos(math.radians(azimuth))*dx, y+math.sin(math.radians(azimuth))*dy, -omega+azimuth, "#0d453a")

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
        coords = x-radius['x'], y+radius['y'], x+radius['x'], y-radius['y']
        arc = self.create_arc(coords, start=azimuth+40, extent=100, fill=color, outline="", stipple="gray50")
        
        # draw line
        endx = x + math.cos(math.radians(azimuth+90))*radius['x']
        endy = y + math.sin(math.radians(azimuth-90))*radius['x']
        line = self.create_line(x, y, endx, endy, fill="black", dash=(4,4))
        # save sensor
        self.sensors.append( {'arc': arc,'line': line} )
    
    def update(self):
        # hide and delete all drawn objects
        for o in self.objects:
            self.itemconfigure(o, state='hidden')
            self.delete(o)
        self.objects = []
        # draw the new objects
        #print("App.update: objects", self.getData())
        for o in self.getData():
            self.objects.append( self.add_object(*o) )
        self.after(500, self.update)
    
    def add_object(self, azimuth, distance):
        #print("App.create_object: azimuth", azimuth, "distance", distance)
        r = 10
        x0,y0 = self.polar2global(azimuth, distance)
        x1,y1 = self.polar2global(azimuth, distance)
        #print("App.create_object: [",x0,y0,"] [",x1, y1,"]")
        return self.create_oval(x0-r, y0+r, x1+r, y1-r, fill="#ffffff")
