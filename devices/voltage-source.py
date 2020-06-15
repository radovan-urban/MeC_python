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
    This is not a big deat since it is a "fake" display anyway

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

class MainApp(tk.Tk):
    def __init__(self, master=None):
        super().__init__()
        self.master = master
        self.geometry("+100+100")
        self.resizable(width=False, height=False)
        self.protocol("WM_DELETE_WINDOW", self.on_quit)

        # Link to volmeter
        self.VM = Voltage_source()
        #<Create front panel and widgets>
        # This also can be a class that inherits from tk.Frame()
        self.create_widgets()
        #<RUN mainloop()>
        self.mainloop()

    def create_widgets(self):
        #<DISPLAY voltage -- fake>
        self.myvar = tk.StringVar()
        self.disp = tk.Label(self, textvariable = self.myvar)
        self.disp.pack(side="bottom")
        #<CONTROL voltage>
        self.var = tk.DoubleVar()
        self.cntr = tk.Entry(self, textvariable = self.var)
        self.cntr.bind('<Return>', self.cmd)
        self.cntr.pack(side="bottom")
        #<QUIT button>
        self.but_quit = tk.Button(self, text="QUIT", fg="red", command=self.on_quit)
        self.but_quit.pack(side="right", padx=10, pady=10)

        self.update_display()

    def update_display(self):
        update_period = 250    # time in [miliseconds]
        noise = gauss(0, .01)
        self.myvar.set( "{0:9.3f}".format(self.var.get() + noise) )
        self.after(update_period, self.update_display)

    def cmd(self, *args):
        self.focus()  # remove focus from CONTROL
        voltage = self.var.get()
        ivolt = int( 4096/10*voltage )
        print("Entered value = {0}.  DAC input = {1}".format( voltage, ivolt))
        self.VM.set_voltage(ivolt)

    def on_quit(self):
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
    root = MainApp()

if __name__ == "__main__":
    main()

# EOF
