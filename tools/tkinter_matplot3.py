import tkinter as tk
import matplotlib
from matplotlib.backends.backend_tkagg import (
        FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.figure import Figure

class Application(tk.Frame):
    def __init__(self, master=None):
        matplotlib.use('TkAgg')
        tk.Frame.__init__(self, master)
        self.pack()
        self.createWidgets()



    def createWidgets(self):

        self.fig = Figure(figsize=(5,4), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.fig, self)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=0, columnspan=3)



        self.QUIT = tk.Button(self, text="QUIT", fg="red",
                                            command=root.destroy)
        self.QUIT.grid(row=2)

root = tk.Tk()
app = Application(master=root)
app.mainloop()
