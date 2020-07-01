#!/usr/bin/python3

import tkinter as tk

class Checkbar(tk.Frame):
   def __init__(self, parent=None, picks=[], side=tk.LEFT, anchor=tk.W):
      tk.Frame.__init__(self, parent)
      self.vars = []
      for pick in picks:
         var = tk.IntVar()
         chk = tk.Checkbutton(self, text=pick, variable=var)
         chk.pack(side=side, anchor=anchor, expand=tk.YES)
         self.vars.append(var)
   def state(self):
      return map((lambda var: var.get()), self.vars)


if __name__ == '__main__':
   root = tk.Tk()
   lng = Checkbar(root, ['Python', 'Ruby', 'Perl', 'C++'])
   tgl = Checkbar(root, ['English','German'])
   lng.pack(side=tk.TOP,  fill=tk.X)
   tgl.pack(side=tk.LEFT)
   lng.config(relief=tk.GROOVE, bd=2)

   def allstates():
      print(list(lng.state()), list(tgl.state()))
   tk.Button(root, text='Quit', command=root.quit).pack(side=tk.RIGHT)
   tk.Button(root, text='Peek', command=allstates).pack(side=tk.RIGHT)
   root.mainloop()
