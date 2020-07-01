"""
Examples from web:
https://stackoverflow.com/questions/31549613/displaying-a-matplotlib-bar-chart-in-tkinter
https://matplotlib.org/3.1.0/gallery/user_interfaces/embedding_in_tk_sgskip.html


"""

import tkinter as tk

from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
# Implement the default Matplotlib key bindings.
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np
import sys, os
""" add ./devices to python path """
sys.path.append(os.path.expanduser("./devices"))
import device_communicator as dc
import cv2

#print("File location: {}".format(module.__file___))
print("File: ", os.path.dirname(os.path.abspath(__file__)))

class PlotFrame(tk.Frame):
    pass



class MainApp(tk.Tk):
    def __init__(self, parent=None, title="Device",
            FLAG=False, kq=None, chc=None):
        super().__init__()
        self.title(title)
        self.parent = parent
        self.FLAG = FLAG

        self.amp = tk.DoubleVar()
        self.amp.set(0)
        self.sld = tk.Scale(self, from_=0, to=10, orient="horizontal", resolution=.01, label="amplitude", variable=self.amp)
        self.sld.pack(side="top", fill="x", expand=1)

        """
        Matplotplib stuff comes here
        """
        self.fig = Figure(figsize=(5, 4), dpi=100)

        t = np.arange(0, 3, .01)
        self.ax = self.fig.add_subplot(111)
        y=self.amp.get() * np.sin(2 * np.pi * t)
        self.line, = self.ax.plot(t, y, 'r-')
        #self.ax.plot(t, self.amp.get() * np.sin(2 * np.pi * t))

        self.canvas = FigureCanvasTkAgg(self.fig, master=self)  # A tk.DrawingArea.
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        self.toolbar = NavigationToolbar2Tk(self.canvas, self)
        self.toolbar.update()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        self.canvas.mpl_connect("key_press_event", self.on_key_press)
        """
        Eventually this should be a class
        """


        self.lbl = tk.Label(self, text="Number")
        self.lbl.pack(side="bottom", padx = 10, pady = 10)

        """ <COMMUNICATOR> """
        if not self.FLAG:
            self.protocol("WM_DELETE_WINDOW", lambda: None)
            """ <Need to pass ROOT to COMMUNICATOR> """
            self.window = self
            self.kq = kq
            self.chc = chc
            self.comm_agent = dc.Dev_communicator(\
                    self.window, self.kq, self.chc, 2.2\
                    )
        else:
            self.protocol("WM_DELETE_WINDOW", self.on_quit)

        #self.update_GUI()
        """ <RUN> """
        self.mainloop()


    def update_GUI(self):
        data_to_send = 1

        t = np.arange(0, 3, .01)

        # option 1
        """
        self.ax.clear()
        self.ax.plot(t, self.amp.get() * np.sin(2 * np.pi * t))
        """
        # option 2
        self.line.set_ydata(self.amp.get() * np.sin(2 * np.pi * t))
        self.canvas.draw()
        self.ax.set_ylim(-self.amp.get()-.1, self.amp.get()+.1)
        self.fig.canvas.flush_events()

        self.lbl['text'] = str(round(data_to_send, 2))
        self.delay = 500
        if not self.FLAG:
            self.comm_agent.send_data(data_to_send)
            self.comm_agent.poll_queue()
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
    root = MainApp(
            parent=None,
            title="Main",
            FLAG=True,
            kq=None,
            chc=None
            )

def my_dev( kill_queue, child_comm ):
    root = MainApp(
            parent=None,
            title="CHILD: Simple",
            FLAG=False,
            kq=kill_queue,
            chc=child_comm
            )


def version():
    print("Simple GUI: version 0.0.0")

if __name__ == "__main__":
    main()

# EOF sim.py

"""

fig = Figure(figsize=(5, 4), dpi=100)
t = np.arange(0, 3, .01)
fig.add_subplot(111).plot(t, 2 * np.sin(2 * np.pi * t))

canvas = FigureCanvasTkAgg(fig, master=root)  # A tk.DrawingArea.
canvas.draw()
canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)

toolbar = NavigationToolbar2Tk(canvas, root)
toolbar.update()
canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)


def on_key_press(event):
    print("you pressed {}".format(event.key))
    key_press_handler(event, canvas, toolbar)


canvas.mpl_connect("key_press_event", on_key_press)

"""
