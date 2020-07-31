#!/bin/python3
# coding: utf-8

'''
DESCRIPTION
===========
    A testing INSTR.  A simple interface makes it easy to test
    other aspects such as communication, pipe/queue issues, etc.

    Coded sometimes in 2019-2020 during the COVID-19 pandemic.
    Authors: R. Urban, J. McMonagle.
'''



import tkinter as tk
import os
import random
import time
import sys
import multiprocessing as mp

class MenuBar(tk.Menu):
    def __init__(self, parent=None):
        #tk.Menu.__init__(self, parent)
        super().__init__(parent)
        self.parent = parent
        fileMenu = tk.Menu(self, tearoff=False)
        self.add_cascade(label="File", underline=0, menu=fileMenu)
        #fileMenu.add_command(label="Exit", underline=1, command=lambda: ConfirmQuit(parent))
        fileMenu.add_command(label="Exit", underline=1, \
                command=self.verified_quit)

        simpleMenu = tk.Menu(self, tearoff=False)
        self.add_cascade(label="Simple", underline=0, menu=simpleMenu)
        simpleMenu.add_command(label="window", command=lambda: None)

        helpMenu = tk.Menu(self, tearoff=False)
        self.add_cascade(label="Help", underline=0, menu=helpMenu)
        helpMenu.add_command(label="About", command=lambda: None)
        helpMenu.add_command(label="Help", command=lambda: None)

    def verified_quit(self):
        if self.parent.conf:
            pass
        else:
            self.parent.on_quit()

class Frame_Front_Panel(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent

        _bg1 = "gray20"
        _fg1 = "gold"
        _wid = 200

        self.config(bg=_bg1)
        self.config(width=_wid)
        self.config(height=200)
        self.config(bd=2)
        self.config(relief="ridge")
        self.grid_propagate(False)     # prevents resizing

        """ Creating all widgets """
        self.value_disp = tk.Label(self, text="Camera settings", bg=_bg1, fg=_fg1)

        """ General grid configuration """
        cc=5
        self.columnconfigure(0, weight=1, pad=cc)
        self.columnconfigure(1, weight=1, pad=cc)
        for i in range(21):
            self.rowconfigure(i, pad=cc)
        self.configure(padx=cc)     # not sure here

        """ Placing all widgets """
        self.value_disp.grid(column=0, columnspan=2, row=0, sticky="new")

class MainApp(tk.Tk):
    def __init__(self, parent=None, title="Device",
            conf=None, kq=None, chc=None, sq=None):
        super().__init__()
        self.title(title)
        self.parent = parent
        self.conf = conf
        self.chc = chc
        self.kq = kq
        self.sq = sq


        """ <COMMUNICATOR> """
        if conf:
            ''' Started from BRIDGE '''
            self.protocol("WM_DELETE_WINDOW", lambda: None)
        else:
            ''' running solo '''
            self.protocol("WM_DELETE_WINDOW", self.on_quit)
            #print("SIMPLE: Creating fake PIPE and QUEUE")
            self.kq = mp.Queue()                            # fake queue

        self.initialization()

        """ Building the interface """
        """ ************************************************************ """
        """ Menus """
        self.config(menu = MenuBar(self))
        self.FrontPanel = Frame_Front_Panel(self)
        self.FrontPanel.grid(column=1, row=0, sticky="ns")
        """ Interface is DONE !!! """

        self.update_GUI()
        """ <RUN> """
        self.mainloop()

    def initialization(self):
        # default values for all possible keys
        print("SIMPLE: getting values from CONFIG ...")
        my_init = {
                'position':'+1+1',
                'variable':'Random',
                'update':1000,
        }

        for k, v in my_init.items():
            try: my_init[k] = self.conf[k]
            except KeyError: pass           # missing key in CONFIG
            except AttributeError: pass     # no CONFIG at all ... solo
            except TypeError: pass          # conf=None

        # declaring a format to send back to bridge
        self.tosend = {}
        self.tosend[my_init['variable']] = float('nan')      # setting a key

        # Assinging varaibles
        self.geometry(my_init['position'])
        self.delay = int(my_init['update'])


    def update_GUI(self):
        # generating data
        data_to_send = str(round(random.uniform(0, 10), 2))
        self.tosend['Random'] = data_to_send
        if self.chc:
            self.chc.send(self.tosend)

        # Updading GUI
        self.FrontPanel.value_disp['text'] = data_to_send
        self.delay = 1001

        # Checking the kill queue
        if not self.kq.empty():
            string_recived = self.kq.get()
            print("CHILD({}): Received {} from kill_queue!"\
                    .format(os.getpid(), string_recived))
            self.on_quit()

        # Update loop
        self.after(self.delay, self.update_GUI)

    def on_quit(self):
        if self.chc:
            self.chc.close()
        self.destroy()
        print("SIMPLE: All is said and done ... pipe should be dead!")


""" <MAIN BODY> """
# FLAG: True is main | False is child
def main():
    root = MainApp(
            parent=None,
            title="Main",
            conf=None,
            kq=None,
            chc=None,
            sq=None
            )

"""
Test: to be called from main.py
Only creates GUI interface; no communication.
Does not end properly ... yet!
"""
def my_dev( conf_sect, kill_queue, child_comm, save_queue ):
    root = MainApp(
            parent=None,
            title="CHILD: Simple",
            conf=conf_sect,
            kq=kill_queue,
            chc=child_comm,
            sq=save_queue
            )


def version():
    print("Simple GUI: version 0.0.0")

if __name__ == "__main__":
    main()

# EOF sim.py
