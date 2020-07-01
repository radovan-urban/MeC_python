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
import sys
import os

from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
# Implement the default Matplotlib key bindings.
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure

import configparser

import device_communicator as dc        # might pick up different name

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
        deviceMenu.add_command(label="Win position", command=\
                lambda: self.parent.stat_info.set("ID: {} | Geometry: {}"\
                .format(self.parent.winfo_id(), self.parent.geometry())))

        helpMenu = tk.Menu(self, tearoff=False)
        self.add_cascade(label="Help", underline=0, menu=helpMenu)
        helpMenu.add_command(label="About", command=lambda: None)
        helpMenu.add_command(label="Help", command=lambda: None)

class Volt_Graph(tk.Frame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent

        _width, _height = 350, 150

        self.config(bg="red")
        self.config(width=_width)
        self.config(height=_height)
        self.config(bd=2)
        self.config(relief="ridge")
        self.grid_propagate(False)

        _dpi = 72
        _fig_x = _width/_dpi
        _fig_y = _height/_dpi

        fig_frame = Figure(figsize=(_fig_x,_fig_y), dpi=_dpi)
        ax = fig_frame.add_subplot(111)
        _x = [0, 1, 2, 3, 4, 5, 6, 7, 8]
        _y = [0, 1, 4, 9, 16, 25, 36, 49, 64]
        ax.scatter(_x, _y)

        canvas = FigureCanvasTkAgg(fig_frame, self)
        canvas.draw()       # not sure if this is needed
        canvas.get_tk_widget().grid(column=0, row=0, sticky='news')

        self.hist_size = 100    # number of data points

        """ Skip toolbar for now ... frame is too small """
        """
        toolbar = NavigationToolbar2Tk(canvas, self)
        toolbar.update()
        canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)
        """



class Main_GUI(tk.Frame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        bg1="darkgrey"
        self.config(bg=bg1)
        self.config(width=350)
        self.config(height=55)
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
        Slabel = tk.Label(self, text="Soft voltage limit [V]: ", bg=bg1)
       # Voltage Control
        self.V_str = tk.StringVar()
        self.V_str.set(parent.GUIvoltage.get())
        self.SetV = tk.Entry(self, textvariable = self.V_str, width=15)
        self.SetV.bind('<Return>', self.set_volt_GUI)
        self.SetV.bind('<Key Up>', self.arrow_up)
        self.SetV.bind('<Key Down>', self.arrow_down)
        #self.SetV.bind('<Button-1>', self.left_click)

        self.SetS = tk.Entry(self, text="1001001", width=15)

        # Placing Labels
        Vlabel.grid(column=0, row=1, sticky="w")
        Slabel.grid(column=0, row=2, sticky="w")
        self.SetV.grid(column=3, row=1, sticky="e")
        self.SetS.grid(column=3, row=2, sticky="e")


    def set_volt_GUI(self, event):
        self.focus()
        old_value = self.parent.GUIvoltage.get()
        old = str(old_value)
        new = self.V_str.get()
        print("OV, O, N: ", old_value, old, new)
        try:
            new_value = float(new)
            new_value = int(new_value)
            if new_value < 0:
                new_value = 0
            if (new_value - old_value) > 1000:
                new_value = old_value
            if new_value > self.parent.MAX_V:
                new_value = self.parent.MAX_V
            self.parent.GUIvoltage.set(new_value)
            self.V_str.set(str(new_value))
            self.parent.VM.set_voltage( self.parent.GUIvoltage.get() )
        except ValueError:
            print("Invalid number ... keeping old value")
            self.V_str.set(old)
            self.parent.stat_info.set("Invalid entry. Kept old value.")


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
            self.parent.VM.set_voltage( self.parent.GUIvoltage.get() )

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
        self.parent.VM.set_voltage( self.parent.GUIvoltage.get() )

    def left_click(self, event):
        self.focus()            # release focus

class StatusLine(tk.Frame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        bg1="lightgrey"
        self.config(bg=bg1)
        self.config(width=350)
        self.config(height=25)
        self.config(bd=2)
        self.config(relief="sunken")
        self.grid_propagate(False)

        stat_info = tk.Label(self, textvariable=parent.stat_info)
        stat_info.grid(column=0, row=0, sticky="we")

class MainApp(tk.Tk):
    def __init__(self, parent=None, title="default", position="+100+100",
            FLAG=True, kq=None, chc=None):
        super().__init__()      # initializing Tk itself
        self.parent = parent
        self.title(title)
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
            self.cfg_file = filedialog.askopenfilename(initialdir=".",\
                    title="Select config file",
                    filetypes=(("cfg files","*.cfg"),("all files","*.*")))
        else:
            self.protocol("WM_DELETE_WINDOW", self.on_quit)
            # if running solo open config file
            self.cfg_file = filedialog.askopenfilename(initialdir=".",\
                    title="Select config file",
                    filetypes=(("cfg files","*.cfg"),("all files","*.*")))
        # </HW & communication>

        self.initialization()

        """ Building the interface """
        """ ************************************************************ """
        self.MENU = MenuBar(self)
        #self.config(menu = MenuBar(self))
        self.config(menu = self.MENU)

        # Loads GUI interface into main window
        self.VoltmeterGUI = Main_GUI(self)
        self.VoltmeterGraph = Volt_Graph(self)
        self.Status = StatusLine(self)

        self.VoltmeterGUI.grid(column=0, row=0)
        self.VoltmeterGraph.grid(column=0, row=1)
        self.Status.grid(column=0, row=2)
        """ ************************************************************ """

        #<RUN mainloop()>
        self.update_GUI()
        self.mainloop()

    def initialization(self):
        print("VOLT: Initialization ...")
        """ Default initial values """
        my_init = {
                'position':'+1+1',
                'max_voltage':'60000',
                'soft_limit':'20000',
                'start_voltage':'0',
        }

        # Timing varaibles
        self.update_period = 250        # time in miliseconds

        # Declaring variables
        self.GUIvoltage = tk.IntVar()
        self.GUIvoltage.set(0)

        self.stat_info = tk.StringVar()
        self.stat_info.set("Init voltage source ...")
        self.old_stat = "old"   # any string really ...
        self.status_timer = 0
        status_disp_time = 3    # time in seconds
        self.status_disp_cycles = status_disp_time*1000/self.update_period

        try:
            os.path.isfile(self.cfg_file)           ## check what happens when file is not CFG ??
            self.cfg = configparser.ConfigParser()
            self.cfg.read(self.cfg_file)
            Glassman = self.cfg['Glassman']
            for k, v in my_init.items():
                try:
                    my_init[k] = Glassman[k]
                except KeyError:
                    pass
        except TypeError:
            print("Empty path to cfg file! Default values are used ...")
        except configparser.MissingSectionHeaderError:
            print("Wrong file format! Default values are used ...")

        """ asign values to variables +++++++++++++++++++++ """
        position = my_init['position']
        self.MAX_V = int(my_init['max_voltage'])
        self.SOFT_V = int(my_init['soft_limit'])
        self.GUIvoltage.set(int(my_init['start_voltage']))
        """ +++++++++++++++++++++++++++++++++++++++++++++++ """

        self.geometry(position)
        self.resizable(width=False, height=False)

        # sending should be done from there.
        self.VM.set_voltage( self.GUIvoltage.get() )

    def update_GUI(self):   # Communication
        """ Status line update fun """
        if not self.stat_info.get() == self.old_stat:
            self.status_timer += 1
            if self.status_timer > self.status_disp_cycles:
                self.status_timer = 0
                self.stat_info.set("Running ...")
                self.old_stat = self.stat_info.get()
        """ above can go """
        if not self.FLAG:
            action = self.comm_agent.poll_queue_better()
            if action:
                self.on_quit()
        self.after(self.update_period, self.update_GUI)

    def on_quit(self):
        self.GUIvoltage.set(0)
        print("VOLT: Setting voltage to 0 and closing ...")
        self.VM.set_voltage( self.GUIvoltage.get() )
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
        self.tosend = {"{}".format("V_tip [V]"):"init",
                "{}".format("dummy3"):"init"}

    def set_voltage(self, High_voltage):     # need to add another parameter: High_volt
        High_voltage = self.parent.GUIvoltage.get()
        DAC_voltage = High_voltage/self.parent.MAX_V*10
        ivolt = int( 4096/10*DAC_voltage)
        print("VOLT: HiV: {0}V | dacV: {1}V | dacLevel: {2}"\
                .format(High_voltage, round(DAC_voltage, 2), ivolt))
        self.dac.set_voltage(ivolt)
        self.parent.stat_info.set("New voltage: {}V".format(High_voltage))
        """ send set voltage values to BRIDGE """
        self.tosend['V_tip [V]'] = str(High_voltage)
        if not self.parent.FLAG:
            #self.parent.comm_agent.send_data(High_voltage)
            self.parent.comm_agent.send_data(self.tosend)
        return 0

def main():
    root = MainApp(
            parent=None,
            title="Voltage (PID: {})".format(os.getpid()),
            position="+700+100",
            FLAG=True,      # T: running on its own
            kq=None,
            chc=None
            )

def my_dev(kill_queue, child_comm):
    root = MainApp(
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
