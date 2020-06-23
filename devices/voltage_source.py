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

''' Defining frame classes for GUI '''

class Volt_Graph(tk.Frame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent

        self.config(bg="red")
        self.config(width=350)
        self.config(height=100)
        self.config(bd=2)
        self.config(relief="ridge")
        self.grid_propagate(False)


class Main_GUI(tk.Frame):

    def __init__(self,parent):
        tk.Frame.__init__(self,parent)
        self.parent = parent

        self.config(bg="green")
        self.config(width=350)
        self.config(height=100)
        self.config(bd=2)
        self.config(relief="ridge")
        self.grid_propagate(False)

        ## Initalizing Grid
        self.columnconfigure(0, weight=1, pad=5)
        self.columnconfigure(1, weight=1, pad=5)
        self.columnconfigure(2, weight=2, pad=5)
        # Link to voltmeter class
        self.VM = Voltage_source()
        # Initalizing grid labels
        Vlabel = tk.Label(self, text="Voltage: ", bg="black")
        MVlabel = tk.Label(self, text="Measured Voltage: ", bg="black")
        # Placing Labels
        Vlabel.grid(column=0, row=1, sticky="w")
        MVlabel.grid(column=0, row=3, sticky="w")
        # Fake display voltage > can later become measured voltage
        MeasuredV = tk.Label(self, textvariable = parent.fakev, width=15)
        MeasuredV.grid(column=3, row=3, sticky="e")
        # Voltage Control
        self.GUIvoltage = tk.DoubleVar()
        SetV = tk.Entry(self, textvariable = self.GUIvoltage, width=15)
        SetV.bind('<Return>', self.send_voltage)
        SetV.grid(column=3, row=1, sticky="e")
        # Quit Button
        parent.b_QUIT = tk.Button(self, text="QUIT", fg="red",\
                 command=parent.on_quit)
        parent.b_QUIT.grid(column=1, row=4, sticky="s")

#    def update_display_GUI(self):
#        update_time = 250  # [milliseconds]
#        noise = gauss(0, .01)
#        parent.fakev.set("{0:9.3f}".format(self.GUIvoltage.get() + noise))
#        self.after(update_time, self.update_display_GUI)

    def send_voltage(self, *args):
        self.focus()
        voltage = self.GUIvoltage.get()
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

        # Declaring variables
        self.fakev = tk.DoubleVar()
        self.randomV()

        # Loads GUI interface into main window
        self.VoltmeterGUI = Main_GUI(self)
        self.VoltmeterGraph = Volt_Graph(self)

        self.VoltmeterGUI.grid(column=0, row=0)
        self.VoltmeterGraph.grid(column=0, row=1)

        ## Changes dimensions of entire window
        self.canvas =tk.Canvas(self, width =300, height=200)

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

    def randomV(self):
        update_time = 250  # [Milliseconds]
        noise = gauss(2, .01)
        self.fakev.set("{0:9.3f}".format(noise))
        self.after(update_time, self.randomV)


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
