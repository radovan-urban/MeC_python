import multiprocessing as mp
import os
import sys
from time import sleep
import signal
# import configparser

""" add ./devices to python path """
sys.path.append(os.path.expanduser("./devices"))

try:
    import simple           # just for testing
    import camera           # camera module
    import voltage_source   # voltage source module
except ModuleNotFoundError as err:
    print("ERROR: {}!  Exitting ...".format(err))
    sys.exit(True)

class Read_Config:
    def __init__(self):
        #self.to_run = []
        self.to_run = ['simple','camera', 'voltage_source']
        # Removed voltage_source due to dict error
        """
        There will be more stuff here:
        * specifying a config file
        * parsing the config file
        * etc.
        """

    def Run(self):
        return self.to_run

class Main_Comm:
    def __init__(self):
        mp.set_start_method('spawn')
        self.kill_queue = mp.Queue()
        self.save_queue = mp.Queue()   # Adding Save Queue
        self.p_conns = []
        self.ch_conns = []
        self.processes = []

        configurator = Read_Config()
        self.devices = configurator.Run()

        for pr in self.devices:
            run_me = pr+".my_dev"
            # unidirectional pipe: p_conn <-- ch,conn
            self.p_conn, self.ch_conn = mp.Pipe(duplex=False)
            self.proc = mp.Process(target=eval(run_me), \
                    args=(self.kill_queue, self.ch_conn, self.save_queue,  ))   # Adding SQ
            self.proc.start()
            self.p_conns.append(self.p_conn)
            self.ch_conns.append(self.ch_conn)
            self.processes.append(self.proc)
            """
            print("MAIN: Parent PIPE: {}".format(self.p_conn))
            print("MAIN: {}({}): PIPE: {}".format(
                pr.upper(), self.proc.pid, self.ch_conn))
            """

        self.results = [None] * len(self.processes)

    def Get_devices(self):
        return self.devices

    def Pull_Data(self):
        for i, p_conn in enumerate(self.p_conns):
            while p_conn.poll():
                self.results[i] = p_conn.recv()
        return str(self.results)

    def Camera_Saving(self, reftime):
        self.save_queue.put(reftime)

    def Stop_Devices(self):
        for i in enumerate(self.processes):
            self.kill_queue.put(True)
        """
        for proc in self.processes:
            proc.join()
        """
        delay = 2
        print("MAIN_COMM: Waiting ({}s) for processes to finish ...".\
                format(delay))
        sleep(delay)


class GracefulKiller:
    kill_now = False
    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, signum, frame):
        self.kill_now = True
        print("\n")
        print("Caught an interrupt signal ... cleaning up ...")
        print("Terminating processes ...", process.terminate())
        sys.exit(0)


##################################################################

class Dev_communicator():
    def __init__(self, win, kq, chc, data, sq):    # Added sq : Save Queue
        self.kq = kq
        self.chc = chc
        self.win = win
        self.data = data
        self.mypid = os.getpid()
        self.sq = sq    # Save Queue

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

    def camera_save_queue(self):
        if not self.sq.empty():
            save_string = self.sq.get()
            return save_string
        else:
            return False

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



""" <MAIN> """
def main():
    killer = GracefulKiller()

    communicator = Main_Comm()
    print("Starting to collect data")
    maxrun = 100
    for dummy in range(maxrun):
        communicator.Camera_Saving()
        communicator.Pull_Data()
        sleep(.1)
    communicator.Stop_Devices()

if __name__ == '__main__':
    main()
    print ('''Main thread done.''')



# EOF device_communicator.py
