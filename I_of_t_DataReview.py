import numpy as np
import matplotlib.pyplot as plt
from matplotlib import ticker
plt.rcParams.update({"text.usetex":True})
from scipy.constants import e, h
import tkinter as tk
from tkinter import filedialog
from scipy.signal import savgol_filter
from mpl_toolkits.axes_grid1 import host_subplot
from IPython import get_ipython
get_ipython().run_line_magic("matplotlib", "qt5")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def open_file_dialog():
    """Opens a file dialog window of windows explorer and returns the file path of a selected file as string."""
    root = tk.Tk()
    root.title("File Selection")
    file_path = filedialog.askopenfilename()
    root.destroy()
    if file_path:
        print("Selected file:", file_path)
        return file_path
    else:
        raise ValueError("No file selected.")

class MyReview(tk.Tk):
    """Manages the main window of the Measurement Review program."""
    def __init__(self):
        super().__init__()
        self.title("I(t) Measurement Review")

        # Initialize the index variable
        self.ind = 0  
        # Initialize the data table
        self.data = DATA

        # Create the "Go to measurement No." Buton 
        self.entry = tk.Entry(self)
        self.entry.insert(0,"0")
        self.entry.pack(side=tk.BOTTOM)
        self.button = tk.Button(self, text="Go to:", command=self.set_count)
        self.button.pack(side=tk.BOTTOM)

        # Initialize the Metadata depiction
        self.right_frame = tk.Frame(self)
        self.right_frame.pack(side=tk.RIGHT)
        self.label = tk.Label(self.right_frame, text=self.get_metadata(self.ind), justify="left")
        self.label.pack(side=tk.TOP)
        self.button_print = tk.Button(self.right_frame, text="Save Index", command=self.handle_save)
        self.button_print.pack(side=tk.TOP)

        # Create the input for the used setpoint current
        self.label_2 = tk.Label(self.right_frame, text="Current setpoint\nto calculate I-I_0 [nA]", justify="center")
        self.label_2.pack(side=tk.TOP)
        self.setpoint_entry = tk.Entry(self.right_frame)
        self.setpoint_entry.insert(0,"0.35")
        self.setpoint_entry.pack(side=tk.TOP)
        self.button_setpoint = tk.Button(self.right_frame, text="Set new I_0", command=self.set_izero)
        self.button_setpoint.pack(side=tk.TOP)
        self.label_3 = tk.Label(self.right_frame, text="Bias Voltage\nto calculate G", justify="center")
        self.label_3.pack(side=tk.TOP)
        self.bias_entry = tk.Entry(self.right_frame)
        self.bias_entry.insert(0,"0.6")
        self.bias_entry.pack(side=tk.TOP)
        self.button_bias = tk.Button(self.right_frame, text="Set new U Bias", command=self.set_bias)
        self.button_bias.pack(side=tk.TOP)

        self.setpoint = float(self.setpoint_entry.get())
        self.bias = float(self.bias_entry.get())

        # Initialize the first depicted Figure
        self.fig = Figure(dpi=100,figsize=(16*2/3,9*2/3))
        self.ax_data = self.fig.add_subplot(121)
        self.ax_curr = host_subplot(122,figure=self.fig)
        self.ax_curr.sharey(self.ax_data)
        self.ax_cond = self.ax_curr.twinx()
        self.create_axis(self.ind, self.ax_data, self.ax_curr)
        self.fig.tight_layout()
        self.canvas = FigureCanvasTkAgg(self.fig)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack()

        self.set_izero()
        self.set_bias()

        # Initialize the buton press events for forward and backward 
        self.bind("<Right>", self.handle_next)
        self.bind("<Left>", self.handle_previous)
        self.bind("<Return>", self.handle_return)

    @ticker.FuncFormatter
    def conduction_formatter(x, pos):
        """Formats the additional conductance y-axis ticks."""
        if float(x) != 0:
            a = f'{x:.1e}'
            return r"$" + f"{a[:-4]}" + r"\cdot 10^{" + f"{a[-3]}{a[-1]}" + r"}$"
        else:
            return f"{x:.0f}"
        
    @ticker.FuncFormatter
    def nano_formatter(x, pos):
        """Formats the current y-axis to display [nA]."""
        x = x*1e9
        return f'{x:.2f}'

    def create_axis(self, i:int, ax_0:plt.Axes, ax_1:plt.Axes) -> list[plt.Axes]:
        """Clears the axis and plots it new for the pased index."""
        data = self.data[:,i+1] - self.setpoint
        ax_0.clear()
        ax_0.scatter(np.asarray(range(len(data)))*2160e-6,data,s=7,alpha=0.7)
        ax_0.plot(np.asarray(range(len(data)))*2160e-6,savgol_filter(data,8,1),lw=2)
        ax_0.yaxis.set_major_formatter(self.nano_formatter)
        ax_0.set_xlabel("Time [s]")
        ax_0.set_ylabel("Current [nA]")

        cur = np.asarray(data).T
        counts, edges = np.histogram(cur, bins=250)
        centers = (edges[:-1] + edges[1:]) / 2
        centers = centers[(counts!=0)]
        counts = counts[(counts!=0)]
        ax_1.clear()
        ax_1.step(counts, centers)
        ax_1.yaxis.set_major_formatter(self.nano_formatter)
        ax_1.set_xlabel("Counts")
        xmax = max(counts)

        ax_2 = ax_1.twinx()
        cond = cur/(self.bias * G_0)
        counts, edges = np.histogram(cond, bins=250)
        centers = (edges[:-1] + edges[1:]) / 2
        centers = centers[(counts!=0)]
        counts = counts[(counts!=0)]
        ax_2.step(counts, centers, alpha=0)
        ax_2.yaxis.set_major_formatter(self.conduction_formatter)
        ax_2.set_ylabel("Multiples of G0")
        ax_2.set_xlim((0,xmax*105/100))

    def handle_next(self, event:str) -> None:
        """Sets the curent index +2 if the right arrow is pressed and updates the Figure and Metatda"""
        if event.keysym == "Right":
            self.ind += 2
            if self.ind > len(self.data[0]) -1:
                self.ind = 0
            self.create_axis(self.ind, self.ax_data, self.ax_curr)
            self.canvas.draw()
            self.label.config(text=self.get_metadata(self.ind))

    def handle_previous(self, event:str) -> None:
        """Sets the curent index -2 if the left arrow is pressed and updates the Figure and Metatda"""
        if event.keysym == "Left":
            self.ind -= 2
            if self.ind == -2:
                self.ind = len(self.data[0]) - 2
            self.create_axis(self.ind, self.ax_data, self.ax_curr)
            self.canvas.draw()
            self.label.config(text=self.get_metadata(self.ind))

    def handle_return(self, event:str) -> None:
        """Activates the set_count function if the Enter key is pressed."""
        if event.keysym == "Return":
            self.set_count()

    def handle_save(self):
        """Prints the current file index to the console and saves it for later return."""
        inds.append(self.ind)
        print(f"Saved Index: {self.ind}")

    def set_count(self) -> None:
        """Updates the curent index to the enterd number in "entry" and updates the figure and metadata"""
        try:
            new_ind = int(self.entry.get())
            if new_ind % 2 != 0:
                raise ValueError()
            self.ind = new_ind
            self.create_axis(self.ind, self.ax_data, self.ax_curr)
            self.canvas.draw()
            self.label.config(text=self.get_metadata(self.ind))
        except ValueError:
            print("Invalid input. Please enter a valid integer.")

    def set_izero(self) -> None:
        """Applies the entered current setpoint as offset for the displayed current values"""
        self.setpoint = float(self.setpoint_entry.get()) * 10**(-9)
        self.create_axis(self.ind, self.ax_data, self.ax_curr)
        self.canvas.draw()
        self.label.config(text=self.get_metadata(self.ind))

    def set_bias(self) -> None:
        """Applies the enterd bias voltage on to the conductance calculation."""
        self.bias = float(self.bias_entry.get())
        self.create_axis(self.ind, self.ax_data, self.ax_curr)
        self.canvas.draw()
        self.label.config(text=self.get_metadata(self.ind))

    def get_metadata(self, ind):
        """Constructs the metadata label contend for the current index"""
        info = f"Curent Index: {self.ind}"
        return info

global G_0
G_0 = (2*e**2)/h

global DATA
DATA = np.genfromtxt(open_file_dialog())

global inds
inds = []

window = MyReview()
# Start the tkinter event loop
window.mainloop()
# Returns the saved indeces
print(inds)
