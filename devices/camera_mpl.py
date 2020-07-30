#!/bin/python3
# coding: utf-8

'''
DESCRIPTION
===========
A simple camera-capturng device.  The idea is to run as soon as images
are ready (rather than waiting for GUI to request a frame.



TODOes and ISSUES
=================



Extra info and links:
https://note.nkmk.me/en/python-numpy-image-processing/
https://scipy-lectures.org/advanced/image_processing/
'''

import tkinter as tk
import cv2
import PIL.Image, PIL.ImageTk
import time
import random
import os
import numpy as np

from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
# Implement the default Matplotlib key bindings.
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

import device_communicator as dc




class MenuBar(tk.Menu):
    def __init__(self, parent=None):
        #tk.Menu.__init__(self, parent)
        super().__init__(parent)
        self.parent = parent
        fileMenu = tk.Menu(self, tearoff=False)
        self.add_cascade(label="File", underline=0, menu=fileMenu)
        #fileMenu.add_command(label="Exit", underline=1, command=lambda: ConfirmQuit(parent))
        if parent.FLAG:
            fileMenu.add_command(label="Exit", underline=1, command=parent.on_quit)
        else:
            fileMenu.add_command(label="Exit", underline=1, command=lambda: None)

        deviceMenu = tk.Menu(self, tearoff=False)
        self.add_cascade(label="Camera", underline=0, menu=deviceMenu)
        deviceMenu.add_command(label="Exposure", command=lambda: None)
        deviceMenu.add_command(label="Averaging", command=lambda: None)
        deviceMenu.add_command(label="Binning", command=lambda: None)

        helpMenu = tk.Menu(self, tearoff=False)
        self.add_cascade(label="Help", underline=0, menu=helpMenu)
        helpMenu.add_command(label="About", command=lambda: None)
        helpMenu.add_command(label="Help", command=lambda: None)

class Controls(tk.Frame):
    def __init__(self):
        super().__init__(parent)
        pass

class Frame_Image(tk.Frame):
    def __init__(self, parent=None):
        #tk.Frame.__init__(self, parent)
        super().__init__(parent)
        self.parent = parent

        _bg1 = "midnight blue"
        _fg1 = "yellow"

        self.config(bg=_bg1)
        self.config(width=600)
        self.config(height=500)
        self.config(bd=2)
        self.config(relief="ridge")
        self.grid_propagate(False)     # prevents resizing

        self._vmax = None
        first_image = np.zeros((480,640))

        # Create widgets
        self.sld = tk.Scale(self, from_=0, to=1000, orient="horizontal",\
                resolution=1, label="Exposure level (white point):")
        self.sld_max_label = tk.Label(self, text="Max white level: ",
                bg=_bg1, fg=_fg1)
        self.sld_max = tk.Entry(self, width=10)

        self.fig = Figure(figsize=(5, 4), dpi=100)
        self.ax = self.fig.add_subplot(111, frameon=False)
        #self.img_obj = self.ax.imshow(first_image, vmin=0, vmax=None) #, cmap='Greys_r')
        self.img_obj = self.ax.matshow(first_image, vmin=0, vmax=None) #, cmap='Greys_r')
        self.ax.set_axis_off()
        #self.fig.tight_layout()
        self.fig.subplots_adjust(left=0, bottom=0, right=1, top=1)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self)

        # create layout
        self.columnconfigure(0, weight=1)
        self.rowconfigure(5, weight=1)

        self.sld_max_label.grid(column=0, row=1, sticky='e')
        self.sld_max.grid(column=1, row=1, pady=3, padx=3, sticky='we')
        self.sld.grid(column=0, columnspan=2, row=2, sticky='we')
        self.canvas.get_tk_widget().grid(column=0, columnspan=2, row=5, sticky='sew')

        # bindings
        self.sld.bind('<ButtonRelease-1>', self.on_release)


    def on_release(self, event):
        self._vmax = self.sld.get()
        print("Value: {} and position: {}:{}".format(self._vmax, event.x, event.y))

class Frame_RightNav(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent

        _bg1 = "gray20"
        _fg1 = "gold"
        wid = 200

        self.config(bg=_bg1)
        self.config(width=wid)
        self.config(height=500)
        self.config(bd=2)
        self.config(relief="ridge")
        self.grid_propagate(False)     # prevents resizing

        """ Creating all widgets """
        L_name = tk.Label(self, text="Camera settings", bg=_bg1, fg=_fg1)
        F0 = tk.Frame(self, height=3, width=wid/2+20, bg="black")
        F1 = tk.Frame(self, height=3, width=wid/2-20, bg="white")
        B_temp = tk.Button(self, text="Array info", command=parent.verify_image_array)
        L_avg = tk.Label(self, text="Averaging", bg=_bg1, fg=_fg1)
        B_avg = tk.Checkbutton(self, text="on/off", bg=_bg1, var=parent.chkValue)
        L_frn = tk.Label(self, text="frame rate", bg=_bg1, fg=_fg1)
        L_frv = tk.Label(self, textvariable=parent.frame_rate, width=5)
        L_fran = tk.Label(self, text="frames2avg", bg=_bg1, fg=_fg1)
        self.fr_string = tk.StringVar()
        self.fr_string.set(parent.frames_to_avg.get())
        L_frav = tk.Entry(self, textvariable=self.fr_string, width=5)
        L_frav.bind('<Return>', self.set_frames)

        """ General grid configuration """
        cc=5
        self.columnconfigure(0, weight=1, pad=cc)
        self.columnconfigure(1, weight=1, pad=cc)
        for i in range(21):
            self.rowconfigure(i, pad=cc)
        self.configure(padx=cc)     # not sure here

        """ Placing all widgets """
        L_name.grid(column=0, columnspan=2, row=0, sticky="new")
        F0.grid(column=0, row=1, pady=10, sticky="we")
        F1.grid(column=1, row=1, sticky="we")
        L_avg.grid(column=0, row=5, sticky="e")
        B_avg.grid(column=1, row=5, sticky="w")
        L_frn.grid(column=0, row=7, sticky="e")
        L_frv.grid(column=1, row=7, sticky="w")
        L_fran.grid(column=0, row=8, sticky="e")
        L_frav.grid(column=1, row=8, sticky="w")
        B_temp.grid(column=0, columnspan=2, row=20, sticky="s")

    def set_frames(self, event):
        # takes focus away from Entry widget
        self.focus()

        old_value = str(self.parent.frames_to_avg.get())
        new_value = self.fr_string.get()
        try:
            new = int(new_value)
            if new <= 0:
                print("Number of frames must be above zero!")
                self.fr_string.set("1")
                new=1
            self.parent.frames_to_avg.set(new)
        except ValueError:
            print("Cannot convert to integer!")
            self.fr_string.set(old_value)
        # init video capture
        self.parent.capture_device.init_averaging()




class MainApp_camera(tk.Tk):
    def __init__(self, parent=None, title="default",
            FLAG=False, kq=None, chc=None):
        super().__init__()
        self.parent = parent
        self.FLAG = FLAG

        self.geometry("+100+100")
        self.title(title)

        """ Declaring variables """
        self.frame_rate = tk.DoubleVar()
        self.frame_rate.set(-1)

        self.chkValue = tk.BooleanVar()
        self.chkValue.set(False)

        self.frames_to_avg = tk.IntVar()
        self.frames_to_avg.set(5)

        """ Building the interface """
        """ ************************************************************ """
        """ Menus """
        self.config(menu = MenuBar(self))

        """ Creating frames """
        #self.TopBar = Frame_TopBar(self)
        self.ImageFrame = Frame_Image(self)
        self.RightNav = Frame_RightNav(self)

        self.ImageFrame.grid(column=0, row=0)
        self.RightNav.grid(column=1, row=0, sticky="ns")

        """
        self.canvas = tk.Canvas(self.ImageFrame, width=640, height=480)
        self.canvas.pack(side="left", padx=10, pady=10)
        """

        """ Interface is complete! """


        # <HW & COM>
        self.capture_device = VideoCapture(video_source=0, parent=self)
        if not self.FLAG:
            self.protocol("WM_DELETE_WINDOW", lambda: None)
            self.window = self
            self.kq = kq
            self.chc = chc
            self.comm_agent = dc.Dev_communicator(\
                    self.window, self.kq, self.chc, 1.1)
        else:
            self.protocol("WM_DELETE_WINDOW", self.on_quit)
        # </HW & COM>

        self.update_GUI()
        self.mainloop()

    def update_GUI(self):
        self.delay = 5
        self.fr, answer, frame, aframe = self.capture_device.get_frame()
        #self.lbl_i["text"] = "N/A"
        self.frame_rate.set(round(self.fr, 3))
        if answer:
            self.frame_array = frame    # create class-wide array from cam
            if self.chkValue.get():
                frame = aframe

            _vmax = self.ImageFrame._vmax
            self.ImageFrame.ax.cla()           # .cla or .clear`
            #self.ImageFrame.ax.imshow(frame, vmin=0, vmax=_vmax)     # f. or ax.
            self.ImageFrame.ax.matshow(frame, vmin=0, vmax=_vmax)     # f. or ax.
            self.ImageFrame.ax.set_axis_off()
            self.ImageFrame.canvas.draw()


            """
            self.ImageFrame.img_obj.set_data(frame)
            self.ImageFrame.canvas.draw()
            """

            """
            self.image = PIL.Image.fromarray(frame)   # this can be scalled
            self.photo = PIL.ImageTk.PhotoImage(self.image)
            self.canvas.create_image(0, 0, image = self.photo, anchor = tk.NW)
            """
        # <COMMUNICATOR>
        if self.FLAG:
            # <running stand-alone>
            pass
        else:
            # <running as CHILD>
            action = self.comm_agent.poll_queue_better()
            if action:
                self.on_quit()
            # sending data to BRIDGE should be in DEVICE part
            self.comm_agent.send_data(-random.uniform(0, 10))
        # </COMMINUCATOTR>
        self.after(self.delay, self.update_GUI)

    def verify_image_array(self):
        self.img_np = np.array(self.frame_array, np.float)
        print("Image dimension: {}".format(self.img_np.ndim))
        print("Image array: {}".format(self.img_np.shape))
        print("Array type: {}".format(type(self.img_np)))
        """
        data.astype(np.float64) or np.uint8 or uint16
        """
        print("Number of frame so far: {}".\
                format(self.capture_device.frame_counter))
        print("Averaging variable: {}".format(self.chkValue.get()))
        """
        # conver back to uint8 and save
        pil_img_f = Image.fromarray(im_f.astype(np.uint8))
        pil_img_f.save('data/temp/lena_square_save.png')
        """

    def on_quit(self):
        self.capture_device.release_video()
        print("CAMERA: Video device successfully released ... closing ...")
        self.destroy()

class VideoCapture():
    def __init__(self, video_source=0, parent=None):
        #print("VIDEO: Num of averages: ", parent.frames_to_avg.get())
        self.parent = parent
        self.cap = cv2.VideoCapture(video_source)
        #self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)    # avoid lag. does not work
        if not self.cap.isOpened():
            raise ValueError("Unable to open video ", video_source)
        self.picx = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.picy = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        #print("VIDEO: image size: {}x{}".format(self.picx, self.picy))
        answer, frame = self.cap.read()
        #print("VIDEO: what type is FRAME: ", type(frame))
        self.init_averaging()

    def init_averaging(self):
        self.f_num = self.parent.frames_to_avg.get()
        #print("VIDEO: Init averaging ... frames to average: ", self.f_num)
        # Setting up a frame counter
        self.frame_counter = 0
        self.f_old = 0
        self.t_old = time.time()
        self.frate = -1
        # Setting up averaging
        # !!!!!!!! X and Y are reversed !!!!!!!!!!!!!!!!!!!!!!!
        self.images = np.zeros((self.f_num, self.picy, self.picx))
        print("VIDEO: Images ready for averaging: ", self.images.shape)

    def get_frame(self):
        if self.cap.isOpened():
            answer, frame = self.cap.read()
            if answer:
                frame_np = np.array(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), np.float)
                frame_np = frame_np[np.newaxis,:,:]
                self.frame_counter += 1
                idx = self.frame_counter%self.f_num
                self.images[idx:idx+1,:,:] = frame_np
                frame_avg = np.sum(self.images, axis=0)/self.f_num
                time_diff = time.time() - self.t_old
                if (time_diff) > .5:
                    self.frate = (self.frame_counter-self.f_old)/time_diff
                    self.f_old = self.frame_counter
                    self.t_old = time.time()
                #return self.frate, answer, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                return self.frate, answer, cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), frame_avg
            else:
                return self.frate, answer, None, None
        else:
            return None, False, None, None
    """
    def averge_image(self, frame):
        img_np = np.array(cv2.ctvColor(frame, cv2.COLOR_BGR2GRAY), np.float)
    """

    def release_video(self):
        if self.cap.isOpened():
            self.cap.release()

# <MAIN BODY>
def main():
    root_camera = MainApp_camera(
            parent=None,
            title="Camera (PID: {})".format(os.getpid()),
            FLAG=True,
            kq=None,
            chc=None
            )

def my_dev( kill_queue, child_comm ):
    root_camera = MainApp_camera(
            parent=None,
            title="CHILD: Camera",
            FLAG=False,
            kq=kill_queue,
            chc=child_comm
            )

def version():
    print("CAMERA: version 0")

if __name__ == "__main__":
    main()

# EOF <camera.py>
