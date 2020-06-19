
import tkinter as tk
import tkinter.messagebox

root=tk.Tk()
result=tkinter.messagebox.askquestion('Installation','Do you want to install this anyway?')
if result=='yes':
    theLabel=tk.Label(root,text="Enjoy this software.") #To insert a text
    theLabel.pack()
else:
    root.destroy() #Closing Tkinter window forcefully.
root.mainloop()
