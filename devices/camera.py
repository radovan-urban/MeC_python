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

class Controls(tk.Frame):
    def __init__(self):
        super().__init__(parent)
        pass

class Frame_1(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.config(bg="darkgrey")
        self.config(width=100)
        self.config(height=480)
        self.config(bd=2)
        self.config(relief="ridge")
        self.pack_propagate(False)     # prevents resizing

        """ Elements within """
        parent.b_QUIT = tk.Button(self, text="QUIT",\
                command=parent.on_quit)
        parent.b_QUIT.pack(side="top", padx=5, pady=5, fill="x", expand=True)

        parent.fr_sp1 = tk.Frame(self, height=200, bg="darkgrey")
        parent.fr_sp1.pack(side="top", fill="both", expand=1)

        parent.b_temp = tk.Button(self, text="Array info", \
                command=parent.verify_image_array)
        parent.b_temp.pack(side="top", padx=5, pady=5)

        parent.chkValue = tk.BooleanVar()
        parent.chkValue.set(True)
        parent.chk_avg = tk.Checkbutton(self, text="Avg",
                bg="darkgrey", var=parent.chkValue)
        parent.chk_avg.pack(side="bottom", padx=5, pady=5)
        parent.lbl_f = tk.Label(self, text="frame rate")
        parent.lbl_f.pack(side="bottom", padx=5, pady=5, fill="x", expand=1)

        parent.lbl_i = tk.Label(self, text="frame rate")
        parent.lbl_i.pack(side="bottom", padx=5, pady=5, fill="x", expand=1)


class MainApp_camera(tk.Tk):
    def __init__(self, parent=None, title="default",
            FLAG=False, kq=None, chc=None):
        super().__init__()
        self.parent = parent
        self.FLAG = FLAG

        self.geometry("600x400+100+100")
        self.title(title)

        """ Building interface """
        EF = Frame_1(self)
        #EF.pack(side="right", padx=2, pady=2, fill="x", expand=True)
        EF.pack(side="right", padx=10, pady=10)

        self.canvas = tk.Canvas(self, width=640, height=480)
        self.canvas.pack(side="left", padx=10, pady=10)


        # <HARDWARE>
        self.capture_device = VideoCapture()
        # </HARDWARE>
        # <COMMUNICATOR>
        if not self.FLAG:
            self.b_QUIT["state"] = tk.DISABLED
            self.protocol("WM_DELETE_WINDOW", lambda: None)
            self.window = self
            self.kq = kq
            self.chc = chc
            self.comm_agent = dc.Dev_communicator(\
                    self.window, self.kq, self.chc, 1.1\
                    )
        else:
            self.b_QUIT["state"] = tk.NORMAL
            self.protocol("WM_DELETE_WINDOW", self.on_quit)
        # </COMMUNICATOR>

        self.update_GUI()
        self.mainloop()

    def update_GUI(self):
        self.delay = 5
        if self.chkValue.get():
            pass
        self.fr, answer, frame = self.capture_device.get_frame()
        self.lbl_i["text"] = "N/A"
        self.lbl_f["text"] = str(round(self.fr, 3))
        if answer:
            self.frame_array = frame    # create class-wide array from cam
            self.image = PIL.Image.fromarray(frame)   # this can be scalled
            self.photo = PIL.ImageTk.PhotoImage(self.image)
            self.canvas.create_image(0, 0, image = self.photo, anchor = tk.NW)
        # <COMMUNICATOR>
        if not self.FLAG:
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
    def __init__(self, video_source=0):
        self.cap = cv2.VideoCapture(video_source)
        if not self.cap.isOpened():
            raise ValueError("Unable to open video ", video_source)
        self.picx = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.picy = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        answer, frame = self.cap.read()
        # Setting up a frame counter
        self.frame_counter = 0
        self.f_old = 0
        self.t_old = time.time()
        self.frate = -1


    def get_frame(self):
        if self.cap.isOpened():
            answer, frame = self.cap.read()
            if answer:
                self.frame_counter += 1
                time_diff = time.time() - self.t_old
                if (time_diff) > .5:
                    self.frate = (self.frame_counter-self.f_old)/time_diff
                    self.f_old = self.frame_counter
                    self.t_old = time.time()
                #return self.frate, answer, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                return self.frate, answer, cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            else:
                return self.frate, answer, None
        else:
            return None, False, None

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
