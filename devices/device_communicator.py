import tkinter as tk
import os
import random
import time
import sys
import multiprocessing as mp

class MainApp(tk.Tk):
    def __init__(self, parent=None, title="Device",
            FLAG=False, kq=None, chc=None):
        super().__init__()
        print("CHILD.GUI: Entered __init__")
        """ <Need to pass ROOT to COMMUNICATOR> """
        self.window=self
        
        self.title(title)
        self.b_QUIT = tk.Button(self, text="QUIT", command=self.on_quit)

        self.b_QUIT.pack(side="top", padx=30, pady=30)

        """ <COMMUNICATOR> """
        if not FLAG:
            self.b_QUIT["state"] = tk.DISABLED
            self.protocol("WM_DELETE_WINDOW", lambda: None)

            self.kq = kq
            self.chc = chc
            self.comm_agent = communicator( self.window, self.kq, self.chc )
            self.comm_agent.poll_queue()
        else:
            self.b_QUIT["state"] = tk.NORMAL
            self.protocol("WM_DELETE_WINDOW", self.on_quit)

            
        """ <RUN> """
        self.mainloop()

    def on_quit(self):
        print("Quitting ...")
        self.destroy()

    def dummy(self):
        time.sleep(1)
        print("Dummy ...")
        self.after(100, self.dummy)

class communicator():
    def __init__(self, win, kq, chc):
        self.kq = kq
        self.chc = chc
        self.win = win
        self.mypid = os.getpid()
        print("CHILD {}: kq is {}".format(self.mypid, kq))
    
    def send_data(self):
        randomdata = 2.2
        kill_flag = False
        while not kill_flag:
            randomdata += random.choice(range(10))/10
            self.chc.send(randomdata)
            time.sleep(.5)

    def poll_queue(self):
        #print("CHILD: inside poll_queue function")
        self.chc.send(random.uniform(0, 10))
        if not self.kq.empty():
            kill_flag = self.kq.get()
            print("CHILD {}: Got {} from kill_queue ...".format(self.mypid, kill_flag))
            self.win.on_quit()
        self.win.after(100, self.poll_queue)


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
    print("CHILD: Entered device function")
    print("CHILD: pipe is {}".format(child_comm))
    root = MainApp(
            parent=None,
            title="CHILD", 
            FLAG=False, 
            kq=kill_queue, 
            chc=child_comm
            )


if __name__ == "__main__":
    main()

# EOF sim.py
