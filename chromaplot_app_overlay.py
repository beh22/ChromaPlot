import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.ticker import AutoMinorLocator

class AKdatafile:
    def __init__ (self, datafilename):
        self.datafilename = datafilename
        self.datalines = []
        self.colnoerror = []
        self.colnocheck = []
        self.cc = None
        self.ce = None
        
        try:
            with open(datafilename, 'r') as d:
                self.datalines = d.readlines()
        except:
            with open(datafilename, 'r', encoding='UTF-16') as d:
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

colors = ['k', 'r', 'g', 'b', 'c', 'm']
class chromData:
    def __init__(self, datadic, label, figsize=(7, 3.5), color='k'):
        self.data = datadic
        self.curves = datadic.keys()
        self.fig, self.ax1 = plt.subplots(1, 1, figsize=figsize)
        self.counter = 1

        self.fig = None
        self.ax1 = None
        self.ax2 = None
        self.ax3 = None

        self.colors = plt.rcParams['axes.prop_cycle'].by_key()['color']
        self.curve_colors = {curve: self.colors[i % len(self.colors)] for i, curve in enumerate(self.curves)}

        self.fraction_labels = []
        self.legend_added = False
        self.shaded_regions = []

        self.overlay_colors = {'UV': color}
        self.label = label

    # def listCurves(self):
    #     print(self.curves)
    
    def plotCurve(self, curve, color='k', lw=1, ylabel=None):
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

    def overlayCurves(self, curves, ax):
        max_y = 0
        for curve in curves:
            curvekeys = list(self.data[curve].keys())
            xunits = curvekeys[0]
            yunits = curvekeys[1]
            x = np.array(self.data[curve][xunits])
            y = np.array(self.data[curve][yunits])

            color = self.overlay_colors[curve] if curve in self.overlay_colors else 'k'
            ax.plot(x, y, color=color, label=self.label)

            max_y = max(max_y, max(y))

        ax.set_xlim(left=0, right=max(x))
        ax.set_ylim(bottom=0, top=max_y * 1.03)
        ax.set_xlabel('Volume (mL)')
        ax.set_ylabel('Absorbance (mAU)')
        ax.tick_params(axis='both', labelsize=8)
        ax.xaxis.set_minor_locator(AutoMinorLocator(5))
        ax.legend()

        return ax 

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
        #
        # 
        #  for ax in self.fig.get_axes():
        #      for line in ax.get_lines():
        #          if line.get_label() == curve:
        #              line.remove()  # Remove the line associated with the curve
        #              if ax is self.ax2:
        #                  self.ax2 = None
        #                  ax.cla()
        #                  ax.set_ylabel('')
        #                  ax.yaxis.set_ticks([])
        #                  ax.yaxis.set_ticklabels([])
        #                  self.fig.delaxes(ax)

        #                  # Find the next available axis and set it as ax2
        #                  for next_ax in self.fig.get_axes():
        #                      if next_ax is not self.ax1:
        #                          self.ax2 = next_ax
        #                          break

        #                  # If there is still an ax2 (after reassignment), adjust its position
        #                  if self.ax2:
        #                      self.ax2.spines['right'].set_position(('outward', 40 * (self.counter - 1)))

        #                  # Remove the ax3 if it exists
        #                  for ax3 in self.fig.get_axes():
        #                      if ax3 is not self.ax1 and ax3 is not self.ax2:
        #                          ax3.cla()
        #                          ax3.set_ylabel('')
        #                          ax3.yaxis.set_ticks([])
        #                          ax3.yaxis.set_ticklabels([])
        #                          self.fig.delaxes(ax3)
        #              elif ax is not self.ax1:
        #                  ax.cla()  
        #                  ax.set_ylabel('')  
        #                  ax.yaxis.set_ticks([]) 
        #                  ax.yaxis.set_ticklabels([]) 
        #                  self.fig.delaxes(ax) 

        #  self.fig.canvas.draw()

    def addFractions(self, stript = True, fontsize=6, labheight=5):
        flabx = []
        try:
            f = self.data['Fraction']['ml']
            flab = self.data['Fraction']['Fraction']
        except:
            raise KeyError('Fraction data does not seem to be present')
        
        for i in range(len(flab) - 1):
            flabx.append((f[i] + f[i+1])/2)

        if stript == True: 
            flab = [x.strip("T\"") for x in flab]
        else:
            pass

        for i in range(len(f)):
            if flab[i] == "Waste":
                continue

            line = self.ax1.axvline( x = f[i], ymin = 0,  ymax = 0.05, color = 'red', ls = ':' )
            self.fraction_labels.append(line)

        for i in range(len(flabx)):
            if flab[i] == "Waste":
                continue

            label = self.ax1.text(flabx[i], labheight, flab[i], fontsize = fontsize, ha = 'center')
            self.fraction_labels.append(label)

    def removeFractions(self):
        for label in self.fraction_labels:
            label.remove()
        self.fraction_labels = []

    def addLegend(self):
        handles_labels = [ax.get_legend_handles_labels() for ax in self.fig.get_axes()]
        handles, labels = zip(*handles_labels)
        handles = [item for sublist in handles for item in sublist]
        labels = [item for sublist in labels for item in sublist]
        
        unique_labels = []
        unique_handles = []
        seen_labels = set()

        for handle, label in zip(handles, labels):
            if label not in seen_labels:
                unique_handles.append(handle)
                unique_labels.append(label)
                seen_labels.add(label)

        self.ax1.legend(loc='upper center', bbox_to_anchor=(0.5, 1.12), ncol=10, fontsize=8,
                        handles=unique_handles, labels=unique_labels)
        self.legend_added = True

    def removeLegend(self):
        if self.legend_added:
            self.ax1.legend_.remove()
            self.legend_added = False

    def removeShadedFractions(self):
        for patch in self.shaded_regions:
            patch.remove()
        self.shaded_regions = []

    def clearShadedFractions(self):
        self.removeShadedFractions()
        self.fig.canvas.draw()

    def shadeFractions(self, startFrac, stopFrac, color='gray', alpha=0.5):
        try:
            fractions = self.data['Fraction']['Fraction']
            volumes = self.data['Fraction']['ml']
        except KeyError:
            raise KeyError('Fraction data does not seem to be present')

        fractions = [int(x.strip("T\"")) for x in fractions if x.strip("T\"").isdigit()]

        if startFrac not in fractions or stopFrac not in fractions:
            raise ValueError('Specified fractions are not in the data')

        startIndex = fractions.index(startFrac)
        stopIndex = fractions.index(stopFrac)

        startVol = volumes[startIndex]
        stopVol = volumes[stopIndex]

        # self.removeShadedFractions()

        for ax in self.fig.get_axes():
            if ax is self.ax1:
                xdata, ydata = self.ax1.lines[0].get_data()
                mask = (xdata >= startVol) & (xdata <= stopVol)
                patch = ax.fill_between(xdata[mask], ydata[mask], color=color, alpha=alpha)
                self.shaded_regions.append(patch)

        self.fig.canvas.draw()

    def showPlot(self):
        self.fig.tight_layout()
        plt.show()

    def savePlot(self, outname):
        plt.savefig(outname)

class AktaPlotApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("AKTA Plotting App")

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.create_menu()

    def create_menu(self):
        self.menu_frame = ttk.Frame(self)
        self.menu_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Create a frame for mode selection buttons
        mode_frame = ttk.Frame(self.menu_frame)
        mode_frame.grid(row=0, column=0, columnspan=2, pady=10)

        single_mode_button = ttk.Button(mode_frame, text="Single Mode", command=self.switch_to_single_mode)
        single_mode_button.grid(row=0, column=0, padx=5, pady=5)

        overlay_mode_button = ttk.Button(mode_frame, text="Overlay Mode", command=self.switch_to_overlay_mode)
        overlay_mode_button.grid(row=0, column=1, padx=5, pady=5)

    def switch_to_single_mode(self):
        self.destroy()
        self.quit()
        app = singleMode()
        app.mainloop()
        self.quit()

        # self.withdraw()               # These lines should give a way of going back to main menu when single mode is closed
        # app = singleMode()            # but for some reasons messes with the checkboxes in single mode
        # app.mainloop()
        # self.deiconify()

    def switch_to_overlay_mode(self):
        self.destroy()
        self.quit()
        app = overlayMode()
        app.mainloop()
        self.quit()
    

    def on_closing(self):
        # Ensure script stops running when window is closed
        self.quit()
        self.destroy()
        # if messagebox.askokcancel("Quit", "Do you want to quit?"):
        #     self.quit()
        #     self.destroy()

class singleMode(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("AKTA Plotting App - Single Mode")

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.chrom_data = None
        self.curve_vars = []

        self.add_fraction_labels_var = tk.BooleanVar(value=False)
        self.add_legend_var = tk.BooleanVar(value=False)
        self.shade_fractions_var = tk.BooleanVar(value=False)
        self.start_fraction_var = tk.StringVar(value="")
        self.stop_fraction_var = tk.StringVar(value="")

        self.row = 1

        self.create_widgets()

    def create_widgets(self):
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        head_frame = ttk.Frame(self.main_frame)
        head_frame.grid(row=0, column=0, columnspan=2, padx=5, pady=2, sticky=tk.W)

        self.load_button = ttk.Button(head_frame, text="Load Data", command=self.load_data)
        self.load_button.grid(row=0, column=0, padx=(0, 5), pady=2, sticky=tk.W)

        self.clear_data_button = ttk.Button(head_frame, text="Clear Data", command=self.clear_old_data)
        self.clear_data_button.grid(row=0, column=1, padx=(5, 0), pady=2, sticky=tk.W)

        self.save_button = ttk.Button(self.main_frame, text="Save Plot", command=self.save_plot)
        self.save_button.grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)

        self.checkboxes_frame = ttk.Frame(self.main_frame)
        self.checkboxes_frame.grid(row=1, column=0, padx=5, pady=5, sticky=tk.NW)

        self.plot_frame = ttk.Frame(self.main_frame)
        self.plot_frame.grid(row=1, column=2, padx=5, pady=5, sticky=tk.NE)

    def load_data(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt"),("ASCII files", "*.asc"), ("All files", "*.*")])
        if not file_path:
            return

        try:
            self.clear_old_data()

            datafile = AKdatafile(file_path)
            data = datafile.genAKdict(1,2)
            self.chrom_data = chromData(data)
            self.plot_initial_curve()
            self.create_checkboxes()
            print(f"Loaded data from {file_path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def clear_old_data(self):
        for widget in self.plot_frame.winfo_children():
            widget.destroy()
        
        self.chrom_data = None
        self.curve_vars = []

        for widget in self.checkboxes_frame.winfo_children():
            widget.destroy()

    def plot_initial_curve(self):
        self.chrom_data.fig.clf()
        self.chrom_data.ax1 = self.chrom_data.fig.add_subplot(1, 1, 1)
        self.chrom_data.plotCurve('UV')  # Assuming 'UV' is the label for the UV curve
        
        # Embed the plot in the Tkinter window
        canvas = FigureCanvasTkAgg(self.chrom_data.fig, master=self.plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # self.update_idletasks()

    def create_checkboxes(self):
        self.row = 2

        for widget in self.checkboxes_frame.winfo_children():
            widget.destroy()

        self.curve_vars = []
        
        ttk.Label(self.checkboxes_frame, text="Curves", font=('TkDefaultFont', 14, 'bold')).grid(row=self.row, column=0, padx=5, pady=5, sticky=tk.W)
        self.row += 1

        for curve in self.chrom_data.curves:
            if curve != 'UV':  # Skip the UV curve
                var = tk.BooleanVar(value=False)
                var.trace_add('write', self.update_plot)
                chk = ttk.Checkbutton(self.checkboxes_frame, text=curve, variable=var)
                chk.grid(row=self.row, column=0, sticky=tk.W, padx=5, pady=2)
                self.curve_vars.append((curve, var))
                self.row += 1

        if self.row > 1:
            ttk.Label(self.checkboxes_frame, text="Options", font=('TkDefaultFont', 14, 'bold')).grid(row=self.row, column=0, padx=5, pady=5, sticky=tk.W)
            self.row += 1

            self.add_fraction_labels_checkbox = ttk.Checkbutton(self.checkboxes_frame, text="Add Fraction Labels", variable=self.add_fraction_labels_var, command=self.update_plot)
            self.add_fraction_labels_checkbox.grid(row=self.row, column=0, padx=5, pady=2, sticky=tk.W)
            self.row += 1

            self.add_legend_checkbox = ttk.Checkbutton(self.checkboxes_frame, text="Add Legend", variable=self.add_legend_var, command=self.update_plot)
            self.add_legend_checkbox.grid(row=self.row, column=0, padx=5, pady=2, sticky=tk.W)
            self.row += 1

            self.add_shade_fractions_checkbox = ttk.Checkbutton(self.checkboxes_frame, text="Shade Fractions", variable=self.shade_fractions_var, command=self.toggle_shade_fractions)
            self.add_shade_fractions_checkbox.grid(row=self.row, column=0, padx=5, pady=2, sticky=tk.W)
            self.row += 1

            self.toggle_shade_fractions()

    def update_plot(self, *args):
        for curve, var in self.curve_vars:
            if var.get():
                self.chrom_data.addCurve(curve)
            else:
                self.chrom_data.removeCurve(curve)
        
        if self.add_fraction_labels_var.get():
            self.chrom_data.addFractions()
        else:
            self.chrom_data.removeFractions()

        if self.add_legend_var.get():
            if not self.chrom_data.legend_added:
                self.chrom_data.addLegend()
        else:
            if self.chrom_data.legend_added:
                self.chrom_data.removeLegend()

        self.chrom_data.fig.canvas.draw()
        # self.update_idletasks()

    def toggle_shade_fractions(self):
        if self.shade_fractions_var.get():
            self.start_fraction_label = ttk.Label(self.checkboxes_frame, text="Start Fraction:")
            self.start_fraction_label.grid(row=self.row, column=0, padx=5, pady=2, sticky=tk.W)
            self.row += 1

            self.start_fraction_entry = ttk.Entry(self.checkboxes_frame, textvariable=self.start_fraction_var)
            self.start_fraction_entry.grid(row=self.row, column=0, padx=5, pady=2, sticky=tk.W)
            self.row += 1

            self.stop_fraction_label = ttk.Label(self.checkboxes_frame, text="Stop Fraction:")
            self.stop_fraction_label.grid(row=self.row, column=0, padx=5, pady=2, sticky=tk.W)
            self.row += 1

            self.stop_fraction_entry = ttk.Entry(self.checkboxes_frame, textvariable=self.stop_fraction_var)
            self.stop_fraction_entry.grid(row=self.row, column=0, padx=5, pady=2, sticky=tk.W)
            self.row += 1

            button_frame = ttk.Frame(self.checkboxes_frame)
            button_frame.grid(row=self.row+8, column=0, columnspan=2, padx=5, pady=2, sticky=tk.W)

            self.shade_button = ttk.Button(button_frame, text="Shade", command=self.shade_fractions)
            self.shade_button.grid(row=0, column=0, padx=(0, 5), pady=2, sticky=tk.W)

            self.clear_button = ttk.Button(button_frame, text="Clear", command=self.clear_shaded_fractions)
            self.clear_button.grid(row=0, column=1, padx=(5, 0), pady=2, sticky=tk.W)

        else:
            if hasattr(self, 'start_fraction_label'):
                self.start_fraction_label.grid_remove()
            if hasattr(self, 'start_fraction_entry'):
                self.start_fraction_entry.grid_remove()
            if hasattr(self, 'stop_fraction_label'):
                self.stop_fraction_label.grid_remove()
            if hasattr(self, 'stop_fraction_entry'):
                self.stop_fraction_entry.grid_remove()
            if hasattr(self, 'shade_button'):
                self.shade_button.grid_remove()
            if hasattr(self, 'clear_button'):
                self.clear_button.grid_remove()

    def shade_fractions(self):
        start_fraction = self.start_fraction_var.get().strip()
        stop_fraction = self.stop_fraction_var.get().strip()

        if not start_fraction or not stop_fraction:
            messagebox.showerror("Error", "Start and stop fractions must be specified")
            return

        try:
            start_fraction = int(start_fraction)
            stop_fraction = int(stop_fraction)
        except ValueError:
            messagebox.showerror("Error", "Fractions must be numeric")
            return

        if start_fraction >= stop_fraction:
            messagebox.showerror("Error", "Start fraction must be less than stop fraction")
            return

        self.chrom_data.shadeFractions(start_fraction, stop_fraction)
        self.chrom_data.fig.canvas.draw()

    def clear_shaded_fractions(self):
        self.chrom_data.clearShadedFractions()

    def save_plot(self):

        if self.chrom_data == None:
            messagebox.showerror("Error", "No data loaded")
        else:
            file_path = filedialog.asksaveasfilename(defaultextension=".pdf",
                                                     filetypes=[("PDF files", "*.pdf"),
                                                                ("PNG files", "*.png"),
                                                                ("All files", "*.*")])
            if file_path:
                self.chrom_data.savePlot(file_path)
                messagebox.showinfo("Save Plot", f"Plot saved successfully at {file_path}")

    def on_closing(self):
        # Ensure script stops running when window is closed
        self.quit()
        self.destroy()
        # if messagebox.askokcancel("Quit", "Do you want to quit?"):
        #     self.quit()
        #     self.destroy()

class overlayMode(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("AKTA Plotting App - Overlay Mode")

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.chrom_data_list = []
        self.curve_vars = []

        self.create_widgets()

    def create_widgets(self):
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        head_frame = ttk.Frame(self.main_frame)
        head_frame.grid(row=0, column=0, columnspan=2, padx=5, pady=2, sticky=tk.W)

        self.load_button = ttk.Button(head_frame, text="Load Data", command=self.load_data)
        self.load_button.grid(row=0, column=0, padx=(0, 5), pady=2, sticky=tk.W)

        self.clear_data_button = ttk.Button(head_frame, text="Clear Data", command=self.clear_old_data)
        self.clear_data_button.grid(row=0, column=1, padx=(5, 0), pady=2, sticky=tk.W)

        self.save_button = ttk.Button(self.main_frame, text="Save Plot", command=self.save_plot)
        self.save_button.grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)

        self.checkboxes_frame = ttk.Frame(self.main_frame)
        self.checkboxes_frame.grid(row=1, column=0, padx=5, pady=5, sticky=tk.NW)

        self.plot_frame = ttk.Frame(self.main_frame)
        self.plot_frame.grid(row=1, column=1, columnspan=2, padx=5, pady=5, sticky=tk.NE)

    def load_data(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt"), ("ASCII files", "*.asc"), ("All files", "*.*")])
        if not file_path:
            return
        
        label = simpledialog.askstring("Input", "Enter label for the dataset:")
        if not label:
            return

        try:
            datafile = AKdatafile(file_path)
            data = datafile.genAKdict(1, 2)

            color = colors[len(self.chrom_data_list) % len(colors)]

            chrom_data = chromData(data, label, color=color)
            self.chrom_data_list.append(chrom_data)
            self.create_checkboxes()
            self.update_plot()                  # Is this needed?
            print(f"Loaded data from {file_path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def update_plot(self):
        for widget in self.plot_frame.winfo_children():
            widget.destroy()

        checked_datasets = [cd for cd, var in self.curve_vars if var.get()]

        if not checked_datasets:
            return

        fig, ax = plt.subplots(figsize=(7, 3.5), dpi=100)

        max_y_overall = 0

        for chrom_data in checked_datasets:
            chrom_data.overlayCurves(['UV'], ax=ax)
            max_y_overall = max(max_y_overall, ax.get_ylim()[1])

        ax.set_xlabel('Volume (mL)')
        ax.set_ylabel('Absorbance (mAU)', fontsize=10)
        ax.set_ylim(bottom=0, top=max_y_overall * 1.03)
        ax.legend()
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)       

    def create_checkboxes(self):
        for widget in self.checkboxes_frame.winfo_children():
            widget.destroy()

        ttk.Label(self.checkboxes_frame, text="Datasets", font=('TkDefaultFont', 14, 'bold')).grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)

        for i, chrom_data in enumerate(self.chrom_data_list):
            if i >= len(self.curve_vars):
                var = tk.BooleanVar(value=False)
                self.curve_vars.append((chrom_data, var))
            else:
                _, var = self.curve_vars[i]

            chk = ttk.Checkbutton(self.checkboxes_frame, text=chrom_data.label, variable=var, command=self.update_plot)
            chk.grid(row=i + 1, column=0, sticky=tk.W, padx=5, pady=2)    
     
    def clear_old_data(self):
        for widget in self.plot_frame.winfo_children():
            widget.destroy()

        self.chrom_data_list = []
        self.curve_vars = []

        for widget in self.checkboxes_frame.winfo_children():
            widget.destroy()

    def save_plot(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".pdf",
                                                 filetypes=[("PDF files", "*.pdf"),
                                                            ("PNG files", "*.png"),
                                                            ("All files", "*.*")])
        if file_path:
            self.plot_frame.fig.savefig(file_path)
            messagebox.showinfo("Save Plot", f"Plot saved successfully at {file_path}")

    def on_closing(self):
        self.quit()
        self.destroy()


if __name__ == "__main__":
    app = AktaPlotApp()
    # app = overlayMode()
    app.mainloop()
