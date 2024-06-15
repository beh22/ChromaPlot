import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.ticker import AutoMinorLocator

class AKdatafile:
    def __init__ (self, datafilename, encoding=None):
        self.datafilename = datafilename
        self.datalines = []
        self.colnoerror = []
        self.colnocheck = []
        self.cc = None
        self.ce = None
        
        if encoding:
            with open(datafilename, 'r', encoding=encoding) as d:
                self.datalines = d.readlines()
        else:
            with open(datafilename, 'r') as d:
                self.datalines = d.readlines()

    def readline (self, inline): 
        word = inline.split('\t')
        colno = len(word)
        colnoerror = False
        if colno % 2 != 0:
            colno = colno - 1
            colnoerror = True
        for i in range(colno):
            word[i] = word[i].rstrip()
        return word, colno, colnoerror

    def initodict (self, inlist, colno, colnoerror):
        odictkeys = []
        for i in range(colno)[::2]:
            odictkeys.append(inlist[i])
            values = [{} for x in range(colno)[::2]]
            odict = dict(zip(odictkeys, values))
        return odictkeys, odict, colno, colnoerror

    def initidict (self, inlist, colno, colnoerror, indictkeys, indict, icols=2):
        for i in range(colno)[::2]:
            keys = [inlist[i], inlist[i+1]]
            values = [[] for x in range(icols)]
            indict[indictkeys[int(i/2)]] = dict(zip(keys, values))
        return colno, colnoerror

    def popcurves(self, inlist, colno, colnoerror, indictkeys, indict):
        for i in range(colno)[::2]:
            if inlist[i] == '' and inlist[i+1] == '':
                pass
            else:
                entry = indictkeys[int(i/2)]
                curvekeys = [*indict[entry].keys()]
                try:
                    value1 = float(inlist[i]) if inlist[i] else None
                except ValueError:
                    value1 = inlist[i] if inlist[i] else None
                try:
                    value2 = float(inlist[i+1]) if inlist[i+1] else None
                except ValueError:
                    value2 = inlist[i+1] if inlist[i+1] else None
                
                if value1 is not None:
                    indict[entry][curvekeys[0]].append(value1)
                if value2 is not None:
                    indict[entry][curvekeys[1]].append(value2)
        return colno, colnoerror

    def genAKdict (self, h1, h2):
        curvelist, odict, cc, ce = self.initodict(*self.readline(self.datalines[h1]))
        self.colnoerror.append(ce)
        self.colnocheck.append(cc)
        cc, ce = self.initidict(*self.readline(self.datalines[h2]), curvelist, odict)
        self.colnoerror.append(ce)
        self.colnocheck.append(cc)
        for line in self.datalines[h2+1:]:
            cc, ce = self.popcurves(*self.readline(line), curvelist, odict)
            self.colnoerror.append(ce)
            self.colnocheck.append(cc)
        self.cc = self.colnocheck.count(self.colnocheck[0]) == len(self.colnocheck)
        self.ce = all(self.colnoerror)
        return odict

class chromData:
    def __init__(self, datadic, figsize=(7, 3.5)):
        self.data = datadic
        self.curves = datadic.keys()
        self.fig, self.ax1 = plt.subplots(1, 1, figsize=figsize)
        self.counter = 1
        self.ax2 = None
        self.ax3 = None
        self.colors = plt.rcParams['axes.prop_cycle'].by_key()['color']
        self.curve_colors = {curve: self.colors[i % len(self.colors)] for i, curve in enumerate(self.curves)}

    # def listCurves(self):
    #     print(self.curves)
    
    def plotCurve (self, curve, color='k', lw=1, ylabel=None):
        curvekeys = list(self.data[curve].keys())
        xunits = curvekeys[0]
        yunits = curvekeys[1]
        x = np.array(self.data[curve][xunits])
        y = np.array(self.data[curve][yunits])

        if color is None:
            color = self.curve_colors[curve]

        self.ax1.plot(x, y, color=color, lw=lw, label=curve)
        self.ax1.set_xlim(left=0, right=max(self.data[curve][xunits]))
        self.ax1.set_ylim(bottom=0)
        self.ax1.set_xlabel('Volume (mL)')
        self.ax1.tick_params(axis='both', labelsize=8)
        minorlocator = AutoMinorLocator(5)
        self.ax1.xaxis.set_minor_locator(minorlocator)
        # if ylabel:
        #     self.ax1.set_ylabel(ylabel, color=color, fontsize=10)
        self.ax1.set_ylabel('Absorbance (mAU)', color=color, fontsize=10)

    def addCurve(self, curve, color=None, lw=1, ylabel=True):
        curvekeys = list(self.data[curve].keys())
        xunits = curvekeys[0]
        yunits = curvekeys[1]
        x = np.array(self.data[curve][xunits])
        y = np.array(self.data[curve][yunits])

        if self.ax2 is None:
            self.ax2 = self.ax1.twinx()
            if color is None:
                color = self.curve_colors[curve]
            self.ax2.plot(x, y, color=color, lw=lw, label=curve)
            self.ax2.tick_params(axis='y', labelsize=8, colors=color)
            self.ax2.set_ylim(bottom=0)
            if ylabel:
                ylabel = curve
                self.ax2.set_ylabel(ylabel, color=color, fontsize=10)
        else:
            ax = self.ax1.twinx()
            if color is None:
                color = color = self.curve_colors[curve]
            ax.plot(x, y, color=color, lw=lw, label=curve)
            ax.tick_params(axis='y', labelsize=8, colors=color)
            ax.set_ylim(bottom=0)
            ax.spines['right'].set_position(('outward', 40 * (self.counter - 1)))
            if ylabel:
                ylabel = curve
                ax.set_ylabel(ylabel, color=color, fontsize=10)
            ax.set_frame_on(True)
            self.counter += 1
    
    def removeCurve(self, curve):
        for ax in self.fig.get_axes():
            for line in ax.get_lines():
                if line.get_label() == curve:
                    line.remove()
                    if ax is self.ax2:
                        self.ax2 = None
                        ax.cla()
                        ax.set_ylabel('')
                        ax.yaxis.set_ticks([])
                        ax.yaxis.set_ticklabels([])
                        self.fig.delaxes(ax)
                    elif ax is not self.ax1:
                        ax.cla()
                        ax.set_ylabel('')
                        ax.yaxis.set_ticks([])
                        ax.yaxis.set_ticklabels([])
                        self.fig.delaxes(ax)
        self.fig.canvas.draw()

    # def removeCurve(self, curve):
    #     for ax in self.fig.get_axes():
    #         for line in ax.get_lines():
    #             if line.get_label() == curve:
    #                 line.remove()  # Remove the line associated with the curve
    #                 if ax is self.ax2:
    #                     self.ax2 = None
    #                     ax.cla()
    #                     ax.set_ylabel('')
    #                     ax.yaxis.set_ticks([])
    #                     ax.yaxis.set_ticklabels([])
    #                     self.fig.delaxes(ax)

    #                     # Find the next available axis and set it as ax2
    #                     for next_ax in self.fig.get_axes():
    #                         if next_ax is not self.ax1:
    #                             self.ax2 = next_ax
    #                             break

    #                     # If there is still an ax2 (after reassignment), adjust its position
    #                     if self.ax2:
    #                         self.ax2.spines['right'].set_position(('outward', 40 * (self.counter - 1)))

    #                     # Remove the ax3 if it exists
    #                     for ax3 in self.fig.get_axes():
    #                         if ax3 is not self.ax1 and ax3 is not self.ax2:
    #                             ax3.cla()
    #                             ax3.set_ylabel('')
    #                             ax3.yaxis.set_ticks([])
    #                             ax3.yaxis.set_ticklabels([])
    #                             self.fig.delaxes(ax3)
    #                 elif ax is not self.ax1:
    #                     ax.cla()  
    #                     ax.set_ylabel('')  
    #                     ax.yaxis.set_ticks([]) 
    #                     ax.yaxis.set_ticklabels([]) 
    #                     self.fig.delaxes(ax) 

    #     self.fig.canvas.draw()

    def showPlot(self):
        self.fig.tight_layout()
        plt.show()

class AktaPlotApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("AKTA Plotting App")

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.chrom_data = None
        self.curve_vars = []
        self.add_fraction_labels_var = tk.BooleanVar(value=False)
        self.add_legend_var = tk.BooleanVar(value=False)

        self.create_widgets()

    def create_widgets(self):
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.load_button = ttk.Button(self.main_frame, text="Load Data", command=self.load_data)
        self.load_button.grid(row=0, column=0, padx=5, pady=5)

        self.checkboxes_frame = ttk.Frame(self.main_frame)
        self.checkboxes_frame.grid(row=1, column=0, padx=5, pady=5, sticky=tk.NW)

        self.plot_frame = ttk.Frame(self.main_frame)
        self.plot_frame.grid(row=1, column=1, padx=5, pady=5, sticky=tk.NE)

    def load_data(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt"),("ASCII files", "*.asc"), ("All files", "*.*")])
        if not file_path:
            return

        try:
            datafile = AKdatafile(file_path)
            data = datafile.genAKdict(1,2)
            self.chrom_data = chromData(data)
            self.plot_initial_curve()
            self.create_checkboxes()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def plot_initial_curve(self):
        self.chrom_data.fig.clf()
        self.chrom_data.ax1 = self.chrom_data.fig.add_subplot(1, 1, 1)
        self.chrom_data.plotCurve('UV')  # Assuming 'UV' is the label for the UV curve
        
        # Embed the plot in the Tkinter window
        canvas = FigureCanvasTkAgg(self.chrom_data.fig, master=self.plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def create_checkboxes(self):
        for widget in self.checkboxes_frame.winfo_children():
            widget.destroy()

        self.curve_vars = []
        
        ttk.Label(self.checkboxes_frame, text="Curves", font=('TkDefaultFont', 14, 'bold')).grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        
        row = 1
        for curve in self.chrom_data.curves:
            if curve != 'UV':  # Skip the UV curve
                var = tk.BooleanVar(value=False)
                var.trace_add('write', self.update_plot)
                chk = ttk.Checkbutton(self.checkboxes_frame, text=curve, variable=var)
                chk.grid(row=row, column=0, sticky=tk.W, padx=5, pady=2)
                self.curve_vars.append((curve, var))
                row += 1

        if row > 1:
            ttk.Label(self.checkboxes_frame, text="Options", font=('TkDefaultFont', 14, 'bold')).grid(row=row, column=0, padx=5, pady=5, sticky=tk.W)
            row += 1
            self.add_fraction_labels_checkbox = ttk.Checkbutton(self.checkboxes_frame, text="Add Fraction Labels", variable=self.add_fraction_labels_var, command=self.update_plot)
            self.add_fraction_labels_checkbox.grid(row=row, column=0, padx=5, pady=2, sticky=tk.W)

            self.add_legend_checkbox = ttk.Checkbutton(self.checkboxes_frame, text="Add Legend", variable=self.add_legend_var, command=self.update_plot)
            self.add_legend_checkbox.grid(row=row+1, column=0, padx=5, pady=2, sticky=tk.W)

    def update_plot(self, *args):
        for curve, var in self.curve_vars:
            if var.get():
                self.chrom_data.addCurve(curve)
            else:
                self.chrom_data.removeCurve(curve)
        
        if self.add_fraction_labels_var.get():
            self.add_fraction_labels()

        if self.add_legend_var.get():
            self.add_legend()

        self.chrom_data.fig.canvas.draw()

    def add_fraction_labels(self):
        pass

    def add_legend(self):
        pass

    def on_closing(self):
        # Ensure script stops running when window is closed
        self.quit()
        self.destroy()

if __name__ == "__main__":
    app = AktaPlotApp()
    app.mainloop()
