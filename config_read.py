import configparser
import sys

cfg = configparser.ConfigParser()

cfg.read('config.cfg')
#cfg.write('updated.cfg')
devices = cfg.sections()
devices_low = [i.lower() for i in devices]      # all lower case
if "bridge" in devices_low:
    ind = devices_low.index('bridge')
else:
    print("Config does not include BRIDGE section. Exiting ...")
    sys.exit(1)

"""
processing BRIDGE
=================
allowed fields are:
    directory
"""
bridge = cfg[devices[ind]]
print(bridge['directory'])

