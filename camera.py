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

class Controls(tk.Frame):
    def __init__(self):
        super().__init__(master)
        pass


class MainApp(tk.Tk):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.geometry("600x400+100+100")
        self.protocol("WM_DELETE_WINDOW", self.on_quit)

        #<HARDWARE: linking to camera>
        self.capture_device = VideoCapture()
        
        #<GUI: building interface>
        #self.ctrl_frame = Controls().pack(side="right")
        
        tk.Button(self, text="EXIT", command=self.on_quit).\
                pack(side="right", padx=10, pady=10)

        self.canvas = tk.Canvas(self, width=640, height=480)
        self.canvas.pack(side="right", padx=10, pady=10)

        # Going live ...
        self.update_GUI()

        #<RUN: main loop>
        self.mainloop()

    def update_GUI(self):
        self.delay = 5
        answer, frame = self.capture_device.get_frame()
        if answer:
            self.image = PIL.Image.fromarray(frame)   # this can be scalled
            self.photo = PIL.ImageTk.PhotoImage(self.image)
            self.canvas.create_image(0, 0, image = self.photo, anchor = tk.NW)

        self.after(self.delay, self.update_GUI)

    def on_quit(self):
        print("Closing things up, HAL ... bye!")
        self.capture_device.release_video()
        self.destroy()


class VideoCapture():
    def __init__(self, video_source=0):
        self.cap = cv2.VideoCapture(video_source)
        if not self.cap.isOpened():
            raise ValueError("Unable to open video ", video_source)
        #
        self.picx = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.picy = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        # test
        answer, frame = self.cap.read()
        print("Image received: {}, size: {}x{}".\
                format(answer, self.picx, self.picy))

    def get_frame(self):
        if self.cap.isOpened():
            answer, frame = self.cap.read()
            if answer:
                return answer, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            else:
                return answer, None
        else:
            return False, None

    def release_video(self):
        print("Releasing camera ...")
        if self.cap.isOpened():
            self.cap.release()


# <MAIN BODY>
def main():
    root = MainApp()

if __name__ == "__main__":
    main()

# EOF <camera.py>
