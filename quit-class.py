#!/bin/python3
# coding: utf-8

'''
DESCRIPTION
===========
Simple template to preven accidental closure of the BRIDGE.
It provides shut-down function to ensure safe exit.
It also disables x button.
Based on Reblochon Masque:
https://stackoverflow.com/questions/51690259/create-a-popup-window-to-confirm-quitting-a-tkinter-app
Also good reads:
https://stackoverflow.com/questions/18067915/what-is-the-purpose-of-master-and-master-none-in-an-init-function-in-python
https://stackoverflow.com/questions/24729119/what-does-calling-tk-actually-do
Menus by Bryan Oakley:
https://stackoverflow.com/questions/3520494/class-menu-in-tkinter-gui
Iconify/withdraw/deiconify reading:
https://stackoverflow.com/questions/22834150/difference-between-iconify-and-withdraw-in-python-tkinter

TO DOes and ISSUES
==================
* Make a large Toplevel pop-up window for Help and About.
    Not much in there yet, but a good start.

'''


import tkinter as tk
from time import sleep

class ConfirmQuit(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.geometry("200x100+100+100")
        self.padding = 10
        tk.Label(self, text="Are you sure you want to quit").\
                pack()
        tk.Button(self, text='confirm', command=lambda: self.on_quit(master), fg='red').\
                pack(side=tk.RIGHT, fill=tk.X, padx=self.padding, pady=self.padding)
        tk.Button(self, text='Nooooo!', command=self.destroy).\
                pack(side=tk.LEFT, fill=tk.X, padx=self.padding, pady=self.padding)

    def on_quit(self, master):
        #<steps before shutting down>
        print("Shutting down, HAL ...")
        sleep(1)
        master.destroy()

class MenuBar(tk.Menu):
    def __init__(self, master=None):
        tk.Menu.__init__(self, master=None)

        fileMenu = tk.Menu(self, tearoff=False)
        self.add_cascade(label="File", underline=0, menu=fileMenu)
        fileMenu.add_command(label="Exit", underline=1, command=lambda: ConfirmQuit(master))

        deviceMenu = tk.Menu(self, tearoff=True)
        self.add_cascade(label="Devices", underline=0, menu=deviceMenu)
        #<This menu should be dynamically created as devices are loaded>
        deviceMenu.add_command(label="Camera", command=lambda: None)
        deviceMenu.add_command(label="Glassman", command=lambda: None)
        deviceMenu.add_command(label="RGA", command=lambda: None)
        deviceMenu.add_command(label="SRS-screen", command=lambda: None)

        helpMenu = tk.Menu(self, tearoff=False)
        self.add_cascade(label="Help", underline=0, menu=helpMenu)
        helpMenu.add_command(label="About", command=lambda: None)
        helpMenu.add_command(label="Help", command=lambda: None)



class MainApp(tk.Tk):
    def __init__(self, master=None, title="MAIN", size="200x200+100+100"):
        super().__init__()
        self.title(title)
        self.geometry(size)
        self.resizable(width=False, height=False)
        #<Also could use withdraw(): no taskbar icon | use deiconify to restore>
        # self.protocol("WM_DELETE_WINDOW", self.iconify)               ## minimize
        self.protocol("WM_DELETE_WINDOW", lambda: None)                 ## do nothing
        # self.protocol("WM_DELETE_WINDOW", lambda: ConfirmQuit(self))  ## confirm close
        tk.Button(self, text='QUIT', command=lambda: ConfirmQuit(self)).\
                pack()

        #menubar = MenuBar(self)
        self.config(menu = MenuBar(self))
        #<RUN mainloop()>
        self.mainloop()


def main():
    #<Can specify "title" and "size" here>
    root = MainApp(title="New")
    #root.mainloop()

if __name__ == "__main__":
    main()

# EOF
