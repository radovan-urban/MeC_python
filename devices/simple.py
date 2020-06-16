import tkinter as tk
import os
import random
import time
import sys

import device_communicator as dc

class MainApp(tk.Tk):
    def __init__(self, parent=None, title="Device",
            FLAG=False, kq=None, chc=None):
        super().__init__()
        self.title(title)
        self.parent = parent
        self.FLAG = FLAG

        self.b_QUIT = tk.Button(self, text="QUIT", command=self.on_quit)
        self.b_QUIT.pack(side="top", padx=70, pady=30, expand=True)

        self.lbl = tk.Label(self, text="Number")
        self.lbl.pack(side="bottom", padx = 10, pady = 10)

        """ <COMMUNICATOR> """
        if not self.FLAG:
            self.b_QUIT["state"] = tk.DISABLED
            self.protocol("WM_DELETE_WINDOW", lambda: None)
            """ <Need to pass ROOT to COMMUNICATOR> """
            self.window = self
            self.kq = kq
            self.chc = chc
            self.comm_agent = dc.Dev_communicator(\
                    self.window, self.kq, self.chc, 2.2\
                    )
        else:
            self.b_QUIT["state"] = tk.NORMAL
            self.protocol("WM_DELETE_WINDOW", self.on_quit)

        self.update_GUI()
        """ <RUN> """
        self.mainloop()


    def update_GUI(self):
        data_to_send = random.uniform(0, 10)
        self.comm_agent.send_data(data_to_send)
        self.lbl['text'] = str(round(data_to_send, 2))
        self.delay = 500
        if not self.FLAG:
            self.comm_agent.poll_queue()
        self.after(self.delay, self.update_GUI)

    def on_quit(self):
        print("SIMPLE: Shutting down and quitting ...")
        self.destroy()


""" <MAIN BODY> """

def main():
    root = MainApp(
            parent=None,
            title="Main",
            FLAG=True,
            kq=None,
            chc=None
            )

"""
Test: to be called from main.py
Only creates GUI interface; no communication.
Does not end properly ... yet!
"""
def my_dev( kill_queue, child_comm ):
    #print("CHILD: SIMPLE({}): PIPE: {}".format(os.getpid(), child_comm))
    root = MainApp(
            parent=None,
            title="CHILD: Simple",
            FLAG=False,
            kq=kill_queue,
            chc=child_comm
            )


def version():
    print("Simple GUI: version 0.0.0")

if __name__ == "__main__":
    main()

# EOF sim.py
