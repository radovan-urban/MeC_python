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
        self.to_run = ['simple', 'camera','voltage_source']
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
        self.p_conns = []
        self.ch_conns = []
        self.processes = []

        configurator = Read_Config()
        devices = configurator.Run()

        for pr in devices:
            run_me = pr+".my_dev"
            # unidirectional pipe: p_conn <-- ch,conn
            self.p_conn, self.ch_conn = mp.Pipe(duplex=False)
            self.proc = mp.Process(target=eval(run_me), \
                    args=(self.kill_queue, self.ch_conn, ))
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

    def Pull_Data(self):
        for i, p_conn in enumerate(self.p_conns):
            while p_conn.poll():
                self.results[i] = round(p_conn.recv(), 3)
        print("Data: " + str(self.results)+"           ", end="")
        print("\r", end="")
        return str(self.results)

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
        print("Caught an interrupt signal ... claening up ...")
        print("Terminating processes ...", process.terminate())
        sys.exit(0)


""" <MAIN> """
def main():
    killer = GracefulKiller()

    communicator = Main_Comm()
    print("Starting to collect data")
    maxrun = 100
    for dummy in range(maxrun):
        communicator.Pull_Data()
        sleep(.1)
    communicator.Stop_Devices()

if __name__ == '__main__':
    main()
    print ('''Main thread done.''')

# EOF main.py
