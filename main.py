import multiprocessing as mp
import os
import sys
import time
import signal

"""
To read config file
Uses same structure as in LabView
"""
import configparser

""" add ./devices to python path """
sys.path.append(os.path.expanduser("./devices"))
""" add custom packages """
import sim

procs = 2
result = [None]*procs

def signal_handler(signal, frame):
    print ('\nCaught interrupt, cleaning up...')
    print (process.terminate())
    sys.exit(0)

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


if __name__ == '__main__':
    # this belong to signal_handler function
    #signal.signal(signal.SIGINT, signal_handler)
    
    # this belong to a class
    #killer = GracefulKiller()

    kill_queue = mp.Queue()
    parent_connections = []
    processes = []
    for p in range(procs):
        parent_connection, child_connection = mp.Pipe()
        process = mp.Process(target=sim.my_dev, args=(kill_queue,child_connection,))
        process.start()
        parent_connections.append(parent_connection)
        processes.append(process)
        print("Spawning process with PID:{}".format(process.pid) )
    # finite number of runs ...
    for dummy in range(100):
        for i, p_conn in enumerate(parent_connections):
            while p_conn.poll():
                result[i] = p_conn.recv()
        #print("Data: {:8.2f}".format(result), end="")
        print("Data: " + str(result)+"           ", end="")
        #print(['{:.2f}'.format(item) for item in result])
        print("\r", end="")
        time.sleep(.1)
    # Finishing up ... sending a kill signal
    print("\n\n")
    for proc in processes:
        kill_queue.put(True)

    """ These HAVE TO be done separately """
    for proc in processes:
        proc.join()

    print ('''Main thread done.''')
