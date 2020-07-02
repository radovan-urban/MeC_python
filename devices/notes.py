result = ...poll_save_queue()
if result:
    self.save = True
else:
    try:
        self.next_time_to_save = float(result)
    except ValueError:  # ????
        self.save = False
pass
