#!/bin/python3
# coding: utf-8

'''
Simple template to preven accidental closure of the BRIDGE.
It provides shut-down function to ensure safe exit.
It also disables x button.
Based on Reblochon Masque
https://stackoverflow.com/questions/51690259/create-a-popup-window-to-confirm-quitting-a-tkinter-app
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



class MainApp(tk.Tk):
    def __init__(self, title="MAIN", size="200x200+100+100"):
        super().__init__()
        self.title(title)
        self.geometry(size)
        self.resizable(width=False, height=False)
        # self.protocol("WM_DELETE_WINDOW", self.iconify)               ## minimize
        self.protocol("WM_DELETE_WINDOW", lambda: None)                 ## do nothing
        # self.protocol("WM_DELETE_WINDOW", lambda: ConfirmQuit(self))  ## confirm close
        tk.Button(self, text='QUIT', command=lambda: ConfirmQuit(self)).\
                pack()

def main():
    root = MainApp()
    root.mainloop()

if __name__ == "__main__":
    main()

# EOF
