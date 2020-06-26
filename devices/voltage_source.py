#!/bin/python3
# coding: utf-8

'''
DESCRIPTION
===========
This is 0-10V power supply (range depends on a board: Adafruit_MCP4725)
There is also a fake display that takes the set voltage value and adds
noise to it.

Coded sometimes in 2020 during COVID-19 pandemic.
Authors: R. Urban, J. McMonagle
'''

import tkinter as tk
from tkinter import filedialog
import time
from random import gauss
import cv2
import sys
import os

import configparser

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
        self.add_cascade(label="Voltage", underline=0, menu=deviceMenu)
        deviceMenu.add_command(label="Exposure", command=lambda: None)
        deviceMenu.add_command(label="Averaging", command=lambda: None)
        deviceMenu.add_command(label="Win position", command=parent.win_info)

        helpMenu = tk.Menu(self, tearoff=False)
        self.add_cascade(label="Help", underline=0, menu=helpMenu)
        helpMenu.add_command(label="About", command=lambda: None)
        helpMenu.add_command(label="Help", command=lambda: None)



''' Defining frame classes for GUI '''

class Volt_Graph(tk.Frame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent

        self.config(bg="red")
        self.config(width=350)
        self.config(height=150)
        self.config(bd=2)
        self.config(relief="ridge")
        self.grid_propagate(False)


class Main_GUI(tk.Frame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        bg1="darkgrey"
        self.config(bg=bg1)
        self.config(width=350)
        self.config(height=50)
        self.config(bd=2)
        self.config(relief="ridge")
        self.grid_propagate(False)

        ## Initalizing Grid
        rc, cc = 5, 3
        self.columnconfigure(0, weight=1, pad=cc)
        self.columnconfigure(1, weight=1, pad=cc)
        self.columnconfigure(2, weight=2, pad=cc)
        self.rowconfigure(1, pad=rc)

        # Initalizing grid labels
        Vlabel = tk.Label(self, text="High voltage [V]: ", bg=bg1)

        # Placing Labels
        Vlabel.grid(column=0, row=1, sticky="w")

        # Voltage Control
        self.V_str = tk.StringVar()
        self.V_str.set(parent.GUIvoltage.get())
        self.SetV = tk.Entry(self, textvariable = self.V_str, width=15)
        self.SetV.bind('<Return>', self.set_volt_GUI)
        self.SetV.bind('<Key Up>', self.arrow_up)
        self.SetV.bind('<Key Down>', self.arrow_down)
        self.SetV.grid(column=3, row=1, sticky="e")

    def set_volt_GUI(self, event):
        self.focus()
        old_value = self.parent.GUIvoltage.get()
        old = str(old_value)
        new = self.V_str.get()
        try:
            new_value = float(new)
            new_value = int(new_value)
            if new_value < 0:
                new_value = 0
            if (new_value - old_value) > 1000:
                new_value = old_value+1000
            if new_value > self.parent.MAX_V:
                new_value = self.parent.MAX_V
            self.parent.GUIvoltage.set(new_value)
            print("VOLT: Changing voltage to {}".format(self.parent.GUIvoltage.get()))
            self.V_str.set(str(new_value))
            self.parent.VM.set_voltage()
        except ValueError:
            print("Invalid number ... keeping old value")
            self.V_str.set(old)

    def arrow_up(self, event):
        ind = self.SetV.index(tk.INSERT)
        lenstr = len(self.SetV.get())
        multiplier = 10**(lenstr-ind)
        if multiplier <= 1000:
            number = int(self.V_str.get()) + multiplier
            print("Index: {} | Multiplier: {} | New number: {}"\
                    .format(ind, multiplier, number))
            if number < self.parent.MAX_V:
                self.V_str.set(str(number))
                if len(str(number)) > lenstr:
                    self.SetV.icursor(ind+1)
            else:
                number = self.parent.MAX_V
                self.V_str.set(str(number))
                self.focus()

            self.parent.GUIvoltage.set(number)
            print("VOLT: Changing voltage to {}".format(self.parent.GUIvoltage.get()))
            self.parent.VM.set_voltage()

    def arrow_down(self, event):
        ind = self.SetV.index(tk.INSERT)
        lenstr = len(self.SetV.get())
        multiplier = 10**(lenstr-ind)
        number = int(self.V_str.get()) - multiplier
        print("Index: {} | Multiplier: {} | New number: {}"\
                .format(ind, multiplier, number))
        if number > 0:
            self.V_str.set(str(number))
            if len(str(number)) < lenstr:
                self.SetV.icursor(ind-1)
        else:
            number = 0
            self.V_str.set(str(number))
            self.focus()     # relinquish focus

        self.parent.GUIvoltage.set(number)
        print("VOLT: Changing voltage to {}".format(self.parent.GUIvoltage.get()))
        self.parent.VM.set_voltage()

class MainApp_voltage(tk.Tk):
    def __init__(self, parent=None, title="default", position="+100+100",
            FLAG=True, kq=None, chc=None):
        super().__init__()      # initializing Tk itself
        self.parent = parent
        self.FLAG = FLAG        # True=standalone, False=as child

        # <HW & communication>
        self.VM = Voltage_source(parent=self)
        if not self.FLAG:
            self.protocol("WM_DELETE_WINDOW", self.iconify)
            self.window = self
            self.kq = kq
            self.chc = chc
            self.comm_agent = dc.Dev_communicator(\
                    self.window, self.kq, self.chc, 3.3\
                    )
            self.comm_agent.send_data(self.GUIvoltage.get())
        else:
            self.protocol("WM_DELETE_WINDOW", self.on_quit)
            # if running solo open config file
            self.cfg_file = filedialog.askopenfilename(initialdir=".",\
                    title="Select config file",
                    filetypes=(("cfg files","*.cfg"),("all files","*.*")))
        # </HW & communication>


        self.initialization()



        self.geometry(position)   # Sets position on screen
        self.resizable(width=False, height=False)
        self.title(title)

        # Declaring variables
        self.GUIvoltage = tk.IntVar()
        self.GUIvoltage.set(0)

        self.MAX_V = 60000       # voltage calibration .. comes from config


        """ Building the interface """
        """ ************************************************************ """
        self.MENU = MenuBar(self)
        #self.config(menu = MenuBar(self))
        self.config(menu = self.MENU)

        # Loads GUI interface into main window
        self.VoltmeterGUI = Main_GUI(self)
        self.VoltmeterGraph = Volt_Graph(self)

        self.VoltmeterGUI.grid(column=0, row=0)
        self.VoltmeterGraph.grid(column=0, row=1)

        ## Changes dimensions of entire window
        self.canvas =tk.Canvas(self, width =300, height=200)
        """ ************************************************************ """



        #<RUN mainloop()>
        self.update_GUI()
        self.mainloop()

    def initialization(self):
        print("VOLT: Initialization ...")
        to_set = ['position', 'max_voltage', 'soft_limit']
        my_dict = {
                'position':'+1+1',
                'max_voltage':'60000',
                'soft_limit':'20000',
        }

        try:
            os.path.isfile(self.cfg_file)
            self.cfg = configparser.ConfigParser()
            self.cfg.read(self.cfg_file)
            Glassman = self.cfg['Glassman']
            for key in dict(Glassman):
                print("KEY: ", key)
            #print(to_set)
            print(my_dict)
            for k, v in zip(my_dict.keys(),my_dict.values()):
                try:
                    val_read = Glassman[k]
                except KeyError:
                    val_read = v
                print("{} === {}".format(k, val_read))
        except TypeError:
            print("Empty path to cfg file")


    def update_GUI(self):   # Communication
        update_period = 250  # time in [milliseconds]
        if not self.FLAG:
            action = self.comm_agent.poll_queue_better()
            if action:
                self.on_quit()
        self.after(update_period, self.update_GUI)

    def win_info(self):
        self.update()
        #self.update()
        ppp="Window position: +{}+{}".format(self.winfo_x(), self.winfo_y())
        print(ppp)




    def on_quit(self):
        self.GUIvoltage.set(0)
        print("VOLT: Setting voltage to 0 and closing ...")
        self.VM.set_voltage()
        self.destroy()

class Voltage_source():
    def __init__(self, parent=None):
        self.parent = parent
        try:
            self.i2c = busio.I2C(board.SCL, board.SDA)
            self.dac = Adafruit_MCP4725.MCP4725(address=0x60, busnum=1)
        except:
            print("No board detected")
            # create a fake variable that program can run

    def set_voltage(self):
        High_voltage = self.parent.GUIvoltage.get()
        DAC_voltage = High_voltage/self.parent.MAX_V*10
        ivolt = int( 4096/10*DAC_voltage)
        print("VOLT: HiV: {0}V | dacV: {1}V | dacLevel: {2}"\
                .format(High_voltage, DAC_voltage, ivolt))
        self.dac.set_voltage(ivolt)
        """ send set voltage values to BRIDGE """
        if not self.parent.FLAG:
            self.parent.comm_agent.send_data(High_voltage)
        return 0

def main():
    DEBUG = True  # True / False
    root_voltage = MainApp_voltage(
            parent=None,
            title="Voltage (PID: {})".format(os.getpid()),
            position="+700+100",
            FLAG=True,      # T: running on its own
            kq=None,
            chc=None
            )

def my_dev(kill_queue, child_comm):
    DEBUG = True  # True / False
    root_voltage = MainApp_voltage(
        parent=None,
        title="CHILD: VOltage (PID: {})".format(os.getpid()),
        position="+700+100",
        FLAG=False,         # F: started from BRIDGE
        kq=kill_queue,
        chc=child_comm
        )

def version():
    print("Volatge source: version 0.0.0")

if __name__ == "__main__":
    main()

# EOF
