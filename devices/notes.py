"""
poll queue function returns:
action, string1, string2
"SAVE", "247573829294.12", "00012.png"
"START", None, "/home/pi/Documents/Data/2020/W111/001_cooling/"
"STOP", None, None
"""

if result:
    if result == "START":
        pass
    if result == "STOP":
        pass
    if result == "SAVE":
        frame_number = string 
   


result, string = ...poll_save_queue()
if result:
    self.save = True
    # create local log file w/ header
else:
    try:
        self.next_time_to_save = float(result)
    except ValueError:  # ????
        self.save = False
pass


result = ..poll
#where_to_save
if result:
    #save as 00000.png
    if self.save:
        frame_counter += 1
    else:
        self.save = True
