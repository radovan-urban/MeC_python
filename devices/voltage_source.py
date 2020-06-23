#!/bin/python3
# coding: utf-8

'''
DESCRIPTION
===========
This is 0-10V power supply (range depends on a board: Adafruit_MCP4725)
There is also a fake display that takes the set voltage value and adds
noise to it.
'''

'''
TO DOes and ISSUES
==================
* "voltage display" updates before you hit <ENTER>:
    This is not a big deal since it is a "fake" display anyway

* When CONTROL widget has the focus, clicking elsewhere does NOTHING:
    I'd like to mimic LV behaiour:
        clicking elsewhere should:
            enter value
            release focus

* Non-numerical chars in voltage input:
    This really screws it up.  Will need try/except structure.
    The same structure can handle negative numbers, too large jumps, etc.
'''

import tkinter as tk
import time
from random import gauss
import cv2
import sys

import device_communicator as dc

global GUI_voltage
GUI_voltage = 2

try:
    #<HARDWARE>
    import board
    import busio
    import Adafruit_MCP4725
    #</HARDWARE>
except ModuleNotFoundError:
    print ("No hardware present ... simulation mode ...")

class MenuBar(tk.Menu):
    pass

class Controls(tk.Frame):
    def __init__(self):
        super().__init__(parent)
        pass

#########################################
# Making new GUI class for voltage source
#########################################
class Main_GUI(tk.Frame):

    def __init__(self,parent):
        tk.Frame.__init__(self,parent)
        self.config(bg="green")
        self.config(width=50)
        self.config(height=100)
        self.config(bd=2)
        self.config(relief="groove")
        # Link to voltmeter class
        self.VM = Voltage_source()
        # Fake display voltage > can later become measured voltage
        self.fakev = tk.StringVar()
        self.disp = tk.Label(self, textvariable = self.fakev)
        self.disp.pack(side="bottom")
        # Voltage Control
        self.var = tk.DoubleVar()
        self.cntr = tk.Entry(self, textvariable = self.var)
        self.cntr.bind('<Return>', self.send_voltage)
        self.cntr.pack(side="right")
        # Labels
        parent.vlabel = tk.Label(self, text="Voltage:")
        parent.vlabel.pack(side="left", padx=5, pady=5, fill="x", expand=1)
        ### Update Fake Voltage
        self.update_display_GUI()
        # Quit Button
        parent.b_QUIT = tk.Button(self, text="QUIT", fg="red",\
                 command=parent.on_quit)
        parent.b_QUIT.pack(side="bottom", padx=8, pady=4)

    def update_display_GUI(self):
        update_time = 250  # [milliseconds]
        noise = gauss(0, .01)
        self.fakev.set("{0:9.3f}".format(self.var.get() + noise))
        self.after(update_time, self.update_display_GUI)

    def send_voltage(self, *args):
        self.focus()
        voltage = self.var.get()
        ivolt = int( 4096/10*voltage)
        print("Entered value = {0} V  DAC input = {1}".format(voltage, ivolt))
        self.VM.set_voltage(ivolt)


class MainApp_voltage(tk.Tk):
    def __init__(self, parent=None, title="default",
            FLAG=False, kq=None, chc=None):
        super().__init__()
        self.parent = parent
        self.FLAG = FLAG

        self.geometry("+700+100")   # Sets position on screen
        self.resizable(width=False, height=False)
        self.title(title)

        # Loads GUI interface into main window
        EF = Main_GUI(self)
        EF.pack(side="top", padx=5, pady=5)

        ## Changes dimensions of entire window
        self.canvas =tk.Canvas(self, width =80, height=150)
        self.canvas.pack(side="top", padx=10, pady=10)

        # Communication
        if not self.FLAG:
            self.b_QUIT["state"] = tk.DISABLED
            self.protocol("WM_DELETE_WINDOW", lambda: None)
            self.window = self
            self.kq = kq
            self.chc = chc
            self.comm_agent = dc.Dev_communicator(\
                    self.window, self.kq, self.chc, 3.3\
                    )
        else:
            self.b_QUIT["state"] = tk.NORMAL
            self.protocol("WM_DELETE_WINDOW", self.on_quit)

        #<RUN mainloop()>
        self.update_comms()
        self.mainloop()


    def update_comms(self):   # Communication
        update_period = 250  # time in [milliseconds]
        if not self.FLAG:
            action = self.comm_agent.poll_queue_better()
            if action:
                self.on_quit()
        self.after(update_period, self.update_comms)


    def on_quit(self):
       self.VM = Voltage_source()
       print("Shutting down ...")
       print("Setting voltage to 0 ...")
       self.VM.set_voltage(0)
       print("Closing the main application window ...")
       self.destroy()


class Voltage_source():
    #<Hardware here>
    def __init__(self):
        try:
            self.i2c = busio.I2C(board.SCL, board.SDA)
            self.dac = Adafruit_MCP4725.MCP4725(address=0x60, busnum=1)
        except:
            print("No board detected")
            # create a fake variable that program can run

    def set_voltage(self, ivolt):
        self.dac.set_voltage(ivolt)

        """
        The return value has to be something meaningful:
        voltage value or image array.  This is the easy
        to pass parameters from backend to GUI.
        """
        return 0


def main():
    #root = tk.Tk()
    print("Voltage Source: Running MAIN")
    root_voltage = MainApp_voltage(
            parent=None,
            title="Main: Voltage",
            FLAG=True,
            kq=None,
            chc=None
            )


def my_dev(kill_queue, child_comm):
    root_voltage = MainApp_voltage(
        parent=None,
        title="CHILD: Voltage",
        FLAG=False,
        kq=kill_queue,
        chc=child_comm
        )

def version():
    print("Volatge source: version 0.0.0")


if __name__ == "__main__":
    main()

# EOF
