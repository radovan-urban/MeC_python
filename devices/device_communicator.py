import tkinter as tk
import os
import random
import time
import sys
#import multiprocessing as mp

class communicator():
    def __init__(self, win, kq, chc, data):
        self.kq = kq
        self.chc = chc
        self.win = win
        self.data = data
        self.mypid = os.getpid()
        print("CHILD: PID is {} and PIPE is {}".format(self.mypid, chc))
    
    def send_data(self):
        # connect to device to send data to main.py
        self.chc.send(self.data)

    def poll_queue(self):
        #print("CHILD: inside poll_queue function")
        #self.chc.send(random.uniform(0, 10))
        self.send_data()
        if not self.kq.empty():
            kill_flag = self.kq.get()
            print("CHILD {}: Got {} from kill_queue ...".format(self.mypid, kill_flag))
            self.win.on_quit()


# EOF device_communicator.py
