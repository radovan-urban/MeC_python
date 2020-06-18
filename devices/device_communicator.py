import os
import sys

class Dev_communicator():
    def __init__(self, win, kq, chc, data):
        self.kq = kq
        self.chc = chc
        self.win = win
        self.data = data
        self.mypid = os.getpid()

    def send_data(self, to_send):
        # connect to device to send data to main.py
        self.chc.send(to_send)

    def poll_queue(self):
        #print("CHILD: inside poll_queue function")
        if not self.kq.empty():
            kill_flag = self.kq.get()
            print("CHILD({}): Got {} from kill_queue ...".\
                    format(self.mypid, kill_flag))
            self.win.on_quit()

    def poll_queue_better(self):
        #print("CHILD: inside poll_queue function")
        if not self.kq.empty():
            kill_flag = self.kq.get()
            print("CHILD({}): Got {} from kill_queue ...".\
                    format(self.mypid, kill_flag))
            #self.win.on_quit()
            return kill_flag
        else:
            return False



# EOF device_communicator.py
