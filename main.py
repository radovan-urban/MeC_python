import multiprocessing as mp
import os
import sys
import time
import signal
#Test Comment on line 6 - JM
"""
To read config file
Uses same structure as in LabView
"""
import configparser

""" add ./devices to python path """
sys.path.append(os.path.expanduser("./devices"))
""" add custom packages """
import simple        # just for testing
import camera

procs = 1

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
        process = mp.Process(target=simple.my_dev, args=(kill_queue,child_connection,))
        process.start()
        parent_connections.append(parent_connection)
        processes.append(process)

    # trying camera
    parent_connection, child_connection = mp.Pipe()
    process = mp.Process(target=camera.my_dev, args=(kill_queue, child_connection, ))
    process.start()
    parent_connections.append(parent_connection)
    processes.append(process)
    # /camera

    # finite number of runs ...
    result = [None]*len(processes)
    for dummy in range(100):
        for i, p_conn in enumerate(parent_connections):
            while p_conn.poll():
                result[i] = p_conn.recv()
        print("Data: " + str(result)+"           ", end="")
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
