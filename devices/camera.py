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

        bg1 = "green"

        self.config(bg=bg1)
        self.config(width=650)
        self.config(height=500)
        self.config(bd=2)
        self.config(relief="ridge")
        self.grid_propagate(False)     # prevents resizing

class Frame_RightNav(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent

        bg1 = "darkgrey"
        wid = 200

        self.config(bg=bg1)
        self.config(width=wid)
        self.config(height=500)
        self.config(bd=2)
        self.config(relief="ridge")
        self.grid_propagate(False)     # prevents resizing

        """ Creating all widgets """
        L_name = tk.Label(self, text="Camera settings", bg=bg1)
        F0 = tk.Frame(self, height=3, width=wid/2+20, bg="black")
        F1 = tk.Frame(self, height=3, width=wid/2-20, bg="white")
        B_temp = tk.Button(self, text="Array info", command=parent.verify_image_array)
        L_avg = tk.Label(self, text="Averaging", bg=bg1)
        B_avg = tk.Checkbutton(self, text="on/off", bg=bg1, var=parent.chkValue)
        L_frn = tk.Label(self, text="frame rate", bg=bg1)
        L_frv = tk.Label(self, textvariable=parent.frame_rate)
        L_fran = tk.Label(self, text="frames2avg", bg=bg1)
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
            FLAG=False, kq=None, chc=None, sq=None):   # Adding save queue
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

        self.record = False
        self.imagename = "undefined.png"
        self.savetime = time.time() * 2

        """ Building the interface """
        """ ************************************************************ """
        """ Menus """
        self.config(menu = MenuBar(self))
        """ Interface is complete! """

        """ Creating frames """
        #self.TopBar = Frame_TopBar(self)
        self.ImageFrame = Frame_Image(self)
        self.RightNav = Frame_RightNav(self)

        self.ImageFrame.grid(column=0, row=0)
        self.RightNav.grid(column=1, row=0, sticky="ns")

        self.canvas = tk.Canvas(self.ImageFrame, width=640, height=480)
        self.canvas.pack(side="left", padx=10, pady=10)


        # <HW & COM>
        self.capture_device = VideoCapture(video_source=0, parent=self)
        if not self.FLAG:
            self.protocol("WM_DELETE_WINDOW", lambda: None)
            self.window = self
            self.kq = kq
            self.chc = chc
            self.sq = sq
            self.comm_agent = dc.Dev_communicator(\
                    self.window, self.kq, self.chc, 1.1, self.sq)
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
            self.image = PIL.Image.fromarray(frame)   # this can be scaled
            self.photo = PIL.ImageTk.PhotoImage(self.image)
            self.canvas.create_image(0, 0, image = self.photo, anchor = tk.NW)
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
            #### Image Saving
            saveaction = self.comm_agent.camera_save_queue()
            if saveaction == False:
                pass
            if isinstance(saveaction, str):
                if saveaction == "start":
                    self.record = True
                elif saveaction == "stop":
                    self.record = False
                else:
                    self.imagename = saveaction
            if isinstance(saveaction, float):
                self.savetime = saveaction
            if self.record == True:
                saveref = self.savetime - time.time()
                if saveref <= 0:
                    self.save_frame(self.imagename)
                    print("CAMERA: Saving now: " + format(time.strftime("%H:%M:%S")))
                    self.savetime = time.time() * 2
        # </COMMUNICATOR>
        self.after(self.delay, self.update_GUI)

    def save_frame(self, fname):
        blankv, answer, frame, blankv2 = self.capture_device.get_frame()
        if answer:
            cv2.imwrite(fname, cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR))

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
        print("Reseting frame_counter ....")
        self.capture_device.frame_counter = 0
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
        if not self.cap.isOpened():
            raise ValueError("Unable to open video ", video_source)
        self.picx = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.picy = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        print("VIDEO: image size: {}x{}".format(self.picx, self.picy))
        answer, frame = self.cap.read()
        print("VIDEO: what type is FRAME: ", type(frame))
        self.init_averaging()

    def init_averaging(self):
        self.f_num = self.parent.frames_to_avg.get()
        print("VIDEO: Init averaging ... frames to average: ", self.f_num)
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

    def averge_image(self, frame):
        img_np = np.array(cv2.ctvColor(frame, cv2.COLOR_BGR2GRAY), np.float)

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
            chc=None,
            sq=None
            )

def my_dev( kill_queue, child_comm, save_queue):
    root_camera = MainApp_camera(
            parent=None,
            title="CHILD: Camera",
            FLAG=False,
            kq=kill_queue,
            chc=child_comm,
            sq=save_queue
            )

def version():
    print("CAMERA: version 0")

if __name__ == "__main__":
    main()

# EOF <camera.py>
