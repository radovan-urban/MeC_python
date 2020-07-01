"""
Examples from web:
https://stackoverflow.com/questions/31549613/displaying-a-matplotlib-bar-chart-in-tkinter
https://matplotlib.org/3.1.0/gallery/user_interfaces/embedding_in_tk_sgskip.html


"""

import tkinter as tk
from PIL import Image
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
# Implement the default Matplotlib key bindings.
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np
import sys, os

print("File: ", os.path.dirname(os.path.abspath(__file__)))

class PlotFrame(tk.Frame):
    pass

class MainApp(tk.Tk):
    def __init__(self, parent=None, title="Device"):
        super().__init__()
        self.title(title)
        self.parent = parent

        self.amp = tk.DoubleVar()
        self.amp.set(1000)
        self.sld = tk.Scale(self, from_=0, to=32000, orient="horizontal",\
                resolution=10, label="amplitude")
        self.sld.pack(side="top", fill="x", expand=1)
        self.sld.bind('<ButtonRelease-1>', self.on_release)



        img = Image.open("/home/pi/Documents/python/MeC.git/tools/00000.png")
        self.img2D = np.asarray(img, dtype="int32")

        """
        Matplotplib stuff comes here
        """
        img = Image.open("/home/pi/Documents/python/MeC.git/tools/00000.png")
        self.img2D = np.asarray(img, dtype="int32")

        self.fig = Figure(figsize=(5, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.imshow(self.img2D)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self)  # A tk.DrawingArea.
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        self.toolbar = NavigationToolbar2Tk(self.canvas, self)
        self.toolbar.update()

        self.canvas.mpl_connect("key_press_event", self.on_key_press)
        """
        Eventually this should be a class
        """

        #self.update_GUI()
        """ <RUN> """
        self.mainloop()

    def on_release(self, event):
        _vmax = self.sld.get()
        print("Slider released with value of {}".format(_vmax))
        self.ax.clear()
        self.ax.imshow(self.img2D, vmin=0, vmax=_vmax)
        self.canvas.draw()

    def update_GUI(self):
        self.delay = 10
        """
        self.ax.clear()
        self.ax.imshow(self.img2D, vmin=0, vmax=self.amp.get())
        self.canvas.draw()
        """
        self.after(self.delay, self.update_GUI)

    def grayConversion(self, image):
        grayValue = 0.07 * image[:,:,2] + 0.72 * image[:,:,1] + 0.21 * image[:,:,0]
        gray_img = grayValue.astype(np.uint8)
        return gray_img

    def on_key_press(self, event):
        print("you pressed {}".format(event.key))
        key_press_handler(event, self.canvas, self.toolbar)

    def on_quit(self):
        print("SIMPLE: Shutting down and quitting ...")
        self.quit()     # stops mainloop
        self.destroy()  # necessary on Windows and some IDEs


""" <MAIN BODY> """

def main():
    root = MainApp(parent=None, title="Main")

if __name__ == "__main__":
    main()

# EOF
