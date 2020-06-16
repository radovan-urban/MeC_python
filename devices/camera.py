#!/bin/python3
# coding: utf-8

'''
DESCRIPTION
===========
A simple camera-capturng device.  The idea is to run as soon as images
are ready (rather than waiting for GUI to request a frame.



TODOes and ISSUES
=================



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
        self.config(bg="red")
        self.config(width=100)
        self.config(height=300)
        self.config(bd=2)
        self.config(relief="ridge")
        self.pack_propagate(False)     # prevents resizing

        """ Elements within """
        parent.b_QUIT = tk.Button(self, text="QUIT",\
                command=parent.on_quit)
        parent.b_QUIT.pack(side="top", padx=10, pady=20)

        parent.b_temp = tk.Button(self, text="Array info", \
                command=parent.verify_image_array)
        parent.b_temp.pack(side="bottom", padx=10, pady=50)




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
        EF.pack(side="right", padx=5, pady=5)

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
        answer, frame = self.capture_device.get_frame()
        if answer:
            self.frame_array = frame    # create class-wide array from cam
            self.image = PIL.Image.fromarray(frame)   # this can be scalled
            self.photo = PIL.ImageTk.PhotoImage(self.image)
            self.canvas.create_image(0, 0, image = self.photo, anchor = tk.NW)
        # <COMMUNICATOR>
        if not self.FLAG:
            self.comm_agent.poll_queue()
            self.comm_agent.send_data(-random.uniform(0, 10))
        # </COMMINUCATOTR>
        self.after(self.delay, self.update_GUI)

    def verify_image_array(self):
        self.img_np = np.array(self.frame_array)
        print("Image array: {}".format(self.img_np.shape))
        print("Array type: {}".format(type(self.img_np)))
        print("Number type: {}".format(type(self.img_np[0,0,0])))
        """
        data.astype(np.float64) or np.uint8 or uint16
        """
        print("Number of frame so far: {}".\
                format(self.capture_device.frame_counter))
        print("Reseting frame_counter ....")
        self.capture_device.frame_counter = 0

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

    def get_frame(self):
        if self.cap.isOpened():
            answer, frame = self.cap.read()
            if answer:
                self.frame_counter += 1
                return answer, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            else:
                return answer, None
        else:
            return False, None

    def release_video(self):
        if self.cap.isOpened():
            self.cap.release()


# <MAIN BODY>
def main():
    print("CAMERA: running MAIN ....")
    root_camera = MainApp_camera(
            parent=None,
            title="Main: Camera",
            FLAG=True,
            kq=None,
            chc=None
            )

def my_dev( kill_queue, child_comm ):
    #print("CAM({}): PIPE: {}".format(os.getpid(), child_comm))
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
