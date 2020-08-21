#!bin/python3
# coding: utf-8

'''
Operating System: Windows
Version: 1
'''

'''
DESCRIPTION:
DAC reading device with visual interface
Using nidaqmx and NI instruments
'''

''' Improvements:
    - Saving to log file
    - Channel selection for different devices
    - No device present error to continue running
'''


import tkinter as tk
import time
import os
import nidaqmx

import device_communicator as dc


class MenuBar(tk.Menu):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent


class Main_GUI(tk.Frame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent

        bg1 = '#88a8fd'
        bd1, rc, cc  = 2, 5, 3

        self.config(bg=bg1)
        self.config(width=300)
        self.config(height=50)
        self.config(bd=bd1)
        self.config(relief="ridge")
        self.grid_propagate(False)

        # Grid
        self.columnconfigure(0, weight=1, pad=cc)
        self.columnconfigure(1, weight=1, pad=cc)
        self.columnconfigure(2, weight=2, pad=cc)

        # Labels
        Vlabel = tk.Label(self, text="Voltage read [V]: ", bg=bg1)
        # Label Control
        Vread = tk.Label(self, textvariable=parent.voltage_read)
        # Placing Labels
        Vlabel.grid(column=0, row=1, sticky="w")
        Vread.grid(column=3, row=1, padx=bd1, pady=bd1, sticky="e")


    def SetSampleRate(self,event):
        self.focus()


class Controls(tk.Frame):
    def __init__(self):
        super().__init__(parent)
        pass


class MainApp_DAC(tk.Tk):
    def __init__(self, parent=None, title="default", position="+100+100",
            FLAG=False, kq=None, chc=None, sq=None):
        super().__init__()
        self.parent = parent
        self.FLAG = FLAG

        self.geometry("+50+50")
        self.title(title)

        '''Variables'''
        self.voltage_read = tk.DoubleVar()
        self.voltage_read.set(0)


        '''
        ******************
        Building Interface
        ******************
        '''

        '''Menu Bar'''
        self.config(menu = MenuBar(self))

        '''Tk frames'''
        self.DAC_GUI = Main_GUI(self)

        self.DAC_GUI.grid(column=0, row=0, padx=1, pady=1)


        ''' Hardware and communication '''
        #self.DAC_Capture = DACCapture( ..., parent=self)
        if not self.FLAG:
            self.protocol("WM_DELETE_WINDOW", lambda: None)
            self.window = self
            self.kq = kq
            self.chc = chc
            self.sq = sq
            self.comm_agent = dc.Dev_communicator(\
                    self.window, self.kq, self.chc, 4.4, self.sq)
        else:
            self.protocol("WM_DEKETE_WINDOW", self.on_quit)

        self.update_GUI()
        self.mainloop()

    def update_GUI(self):
        self.delay = 100
        with nidaqmx.Task() as task:
            task.ai_channels.add_ai_voltage_chan("Dev1/0")
            self.voltage_read.set(round(task.read(), 3))
        ####
        ####
        if self.FLAG:
            # Running on its own
            pass
        else:
            # Running with bridge
            ''' Checking queue for quit command '''
            action = self.comm_agent.poll_queue_better()
            if action:
                self.on_quit()
            ####
        self.after(self.delay, self.update_GUI)

    def on_quit(self):
        print("DAC Read: Recieved kill command... Closing now!")
        self.destroy()


class DACCapture():
    def __init__(self, parent=None):
        self.parent = parent
        ####
        with nidaqmx.Task() as task:
            task.ai_channels.add_ai_voltage_chan("Dev1/0")
            print(task.read())



def main():
    root = MainApp_DAC(
            parent=None,
            title="DAC (PID: {})".format(os.getpid()),
            position="+700+200",
            FLAG=True,
            kq=None,
            chc=None,
            sq=None
            )

def my_dev(kill_queue, child_comm, save_queue):
    root = MainApp_DAC(
        parent=None,
        title="CHILD: DAC (PID: {})".format(os.getpid()),
        position="+700+200",
        FLAG=False,
        kq=kill_queue,
        chc=child_comm,
        sq=save_queue
        )

if __name__ == "__main__":
    main()


#EOF
