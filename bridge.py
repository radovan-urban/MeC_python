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

import main_comm

class ConfirmQuit(tk.Toplevel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        """
        parent.update()
        ppp="{}x{}+{}+{}".format(parent.winfo_width(),
                75,
                parent.winfo_x(),
                parent.winfo_y())
        print(ppp)
        self.geometry(ppp)
        """
        self.title("BRIDGE: Confirm")
        self.padding = 5

        tk.Label(self, text="Are you sure you want to quit").\
                pack(side="top", padx = 70, pady = 30)
        tk.Button(self, text='confirm', command=self.on_quit, fg='red').\
                pack(side=tk.RIGHT, fill=tk.X, padx=self.padding, pady=self.padding)
        tk.Button(self, text='Nooooo!', command=self.destroy).\
                pack(side=tk.LEFT, fill=tk.X, padx=self.padding, pady=self.padding)

    def on_quit(self):
        self.destroy()
        self.parent.on_quit()

class ShowVariables(tk.Toplevel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.title("BRIDGE: Variables")
        self.padding = 20

        self.Top_frame = tk.Frame(self, height=200, width=400, bg="darkgrey")
        self.Top_frame.pack(side="top", padx=5, pady=5)
        self.Bot_frame = tk.Frame(self, height=200, width=400, bg="blue")
        self.Bot_frame.pack(side="bottom", padx=5, pady=5)
        self.Bot_frame.pack_propagate(False)

        self.all_dev_lbl = tk.Label(self.Bot_frame, text=parent.all_dev_str.get())
        self.all_dev_lbl.pack(side="top", fill="x", expand=1)


class MenuBar(tk.Menu):
    def __init__(self, parent=None):
        tk.Menu.__init__(self, parent=None)

        fileMenu = tk.Menu(self, tearoff=False)
        self.add_cascade(label="File", underline=0, menu=fileMenu)
        fileMenu.add_command(label="Exit", underline=1, command=lambda: ConfirmQuit(parent))

        deviceMenu = tk.Menu(self, tearoff=True)
        self.add_cascade(label="Devices", underline=0, menu=deviceMenu)
        #<This menu should be dynamically created as devices are loaded>
        deviceMenu.add_command(label="Show vars", command=lambda: ShowVariables(parent))
        deviceMenu.add_command(label="Camera", command=lambda: None)
        deviceMenu.add_command(label="Glassman", command=lambda: None)
        deviceMenu.add_command(label="RGA", command=lambda: None)
        deviceMenu.add_command(label="SRS-screen", command=lambda: None)

        helpMenu = tk.Menu(self, tearoff=False)
        self.add_cascade(label="Help", underline=0, menu=helpMenu)
        helpMenu.add_command(label="About", command=lambda: None)
        helpMenu.add_command(label="Help", command=lambda: None)

class Frame_1(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.config(bg="red")
        #self.config(width=100)
        self.config(height=150)
        self.config(bd=2)
        self.config(relief="ridge")
        self.pack_propagate(False)     # prevents resizing

        #self.dev_lbl = tk.Label(self, text="Static Init Frame_1")
        self.dev_lbl = tk.Label(self, text="__init__")
        self.dev_lbl.pack(side="top", fill="x", expand=1)

        tk.Button(self,
                text="QUIT",
                command=lambda: ConfirmQuit(parent)).\
                        pack(side="top", padx=10, pady=20, fill="both")

    def update_F1():
        pass


class MainApp(tk.Tk):
    def __init__(self, master=None, title="MAIN", size="222x333+100+100"):
        super().__init__()
        self.title(title)
        self.geometry(size)
        self.resizable(width=False, height=False)
        self.all_dev_str = tk.StringVar()
        #self.all_dev_str.set("Initial string (PARENT)")

        #<Also could use withdraw(): no taskbar icon | use deiconify to restore>
        # self.protocol("WM_DELETE_WINDOW", self.iconify)               ## minimize
        self.protocol("WM_DELETE_WINDOW", lambda: None)                 ## do nothing
        # self.protocol("WM_DELETE_WINDOW", lambda: ConfirmQuit(self))  ## confirm close

        """ Building the interface """
        EF = Frame_1(self).pack(side="top", padx=2, pady=2, fill="x", expand=True)

        #menubar = MenuBar(self)
        self.config(menu = MenuBar(self))

        self.lbl_parent = tk.Label(self, bg="green", text="INIT")
        self.lbl_parent.pack(side="bottom")

        #self.killer = main_comm.GracefulKiller()        # not sure here?!

        print("GUI: Initializing communication ...")
        self.communicator = main_comm.Main_Comm()

        #<RUN mainloop()>
        self.update_GUI()
        self.mainloop()

    def update_GUI(self):
        update_delay = 10
        sleep(.5)
        pulled = self.communicator.Pull_Data()
        self.all_dev_str.set(self.communicator.Pull_Data())
        #self.dev_lbl = tk.Label(self, text=parent.all_dev_str.get())
        #Frame_1(self).dev_lbl = tk.Label(self, text=self.all_dev_str.get())
        self.lbl_parent["text"] = pulled
        Frame_1(self).dev_lbl["text"] = "updated"


        self.after(update_delay, self.update_GUI)

    def on_quit(self):
        print("BRIDGE: Shutting down devices ...")
        self.communicator.Stop_Devices()
        sleep(1)
        print("BRIDGE: HAL, power off GUI ...")
        self.destroy()


def main():
    #<Can specify "title" and "size" here>
    root = MainApp(title="BRIDGE")
    #root.mainloop()

if __name__ == "__main__":
    main()

# EOF
