import tkinter as tk
from tkinter import ttk, colorchooser, messagebox, filedialog
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.ticker import AutoMinorLocator

'''
Bugs to fix:
- UV curve disappears when fractions toggled off if other curves are plotted
- Unticking add legend doesn't remove legend
- Fix plotting for more than 2 curves
- Remove y-axis limits field
- Adding fractions when legend is on removes legend

Potential features to add/change:
- Checkboxes for different curves instead of dropdown menu
    Would probably mean you need to change how curves are added
    (i.e. not plotcurve and addcurve functions)
- Clear plot button
- Better y-axis labelling
- Overlay curves from multiple datasets
- Select or detect encoding, or always convert to same encoding
'''

''' 
AKdatafile class contains methods for converting output ASCII files from 
unicorn into python dictionaries for further manipulation and plotting.

Data structure for dictinoary is a dictionary containing dictionaries for each
pair of volume and variable data (e.g., absorbance and volume etc.) individual
data are stored as lists. Dictinoary keys are taken from column headings in the
import file.

Import data is made into an AKdatafile type object. Object is initialised 
with datafilename, corresponding to the file to be imported, datalines contains
the lines from the import file, with loop structure used to ensure file is 
closed after use. 

Variables such as colnoerror and colnocheck allow certain aspects of the
import file to be tracked on import. Import into python dictionary format is
done by manipulating the datalines object.
'''

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
    
    '''Base function, splits each line by tab delimiters and removes \n 
    characters, generates a list word which is used by other functions to parse
    the data file'''
    def readline (self, inline): 
        word = inline.split('\t')
        colno = len(word)
        colnoerror = False
        if colno%2 !=0:
            colno = colno - 1
            colnoerror = True
        for i in range(colno):
            word[i] = word[i].rstrip()
        return word, colno, colnoerror

    '''Initiates outer dictionary using column headings for the from the 
    extracted line'''
    def initodict (self, inlist, colno, colnoerror):
        odictkeys = []
        for i in range(colno)[::2]:
            odictkeys.append(inlist[i])
            values = [{} for x in range(colno)[::2]]
            odict = dict(zip(odictkeys, values))
        return odictkeys, odict, colno, colnoerror

    '''Initiates inner dictionaries with empty lists, list keys are taken
    from column headins for extracted line'''
    def initidict (self, inlist, colno, colnoerror, indictkeys, indict, 
        icols = 2):
        for i in range(colno)[::2]:
            keys = [inlist[i], inlist[i+1]]
            values = [[] for x in range(icols)]
            indict[indictkeys[int(i/2)]] = dict(zip(keys, values))
        return colno, colnoerror

    '''This fills in the initated lists and ignores blank values, note this 
    code block has issues running properly if UTF16 file format is used 
    directly not sure why. This will also use try and except to convert all
    numerical data into floats, hence faciliate plotting with numpy later'''
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

    '''This puts all the code together two argumnets h1 and h2 are taken which
    specifiy the lines with the column headings that form the keys for the 
    dictionary structures, checks in place to make sure that a) column numbers
    in data are even and b) all lines contain the same number of columns'''
    def genAKdict (self, h1, h2):
        curvelist, odict, cc, ce = self.initodict(*self.readline(
            self.datalines[h1]))
        self.colnoerror.append(ce)
        self.colnocheck.append(cc)
        cc, ce = self.initidict(*self.readline(self.datalines[h2]), 
            curvelist, odict)
        self.colnoerror.append(ce)
        self.colnocheck.append(cc)
        for line in self.datalines[h2+1:]:
            cc, ce = self.popcurves(*self.readline(line), 
                curvelist, odict)
            self.colnoerror.append(ce)
            self.colnocheck.append(cc)
        self.cc = self.colnocheck.count(
            self.colnocheck[0]) == len(self.colnocheck)
        self.ce = all(self.colnoerror)
        return odict


class chromData:
    '''chromdata class is designed to represent a dictionary of the imported data 
    generates from the AKdatafile class as well as the methods required to plot 
    this data'''    

    def __init__(self, datadic, figsize=(7,3.5)):
        self.data = datadic
        self.curves = datadic.keys()
        self.fig, self.ax1 = plt.subplots(1,1,figsize=figsize)
        self.counter = 1

    def listCurves(self):
        print(self.curves)
    
    def plotCurve (self, curve, color = 'k', lw = 1, ylabel=None):
        curvekeys = list(self.data[curve].keys())
        xunits = curvekeys[0]
        yunits = curvekeys[1]
        x = np.array(self.data[curve][xunits])
        y = np.array(self.data[curve][yunits])
        self.ax1.plot(x, y, color=color, lw=lw, label = curve)
        self.ax1.set_xlim(left = 0, right = max(self.data[curve][xunits]))
        self.ax1.set_ylim(bottom = 0) #, max(self.data[curve][yunits])+20)
        self.ax1.set_xlabel('Volume (mL)')
        self.ax1.tick_params(axis = 'both', labelsize = 8)
        minorlocator = AutoMinorLocator(5)
        self.ax1.xaxis.set_minor_locator(minorlocator)
        if ylabel:
            self.ax1.set_ylabel(ylabel, color=color, fontsize=10)

    def addCurve(self, curve, color='g', lw=1, ylim=None, ylabel=None):
        curvekeys = list(self.data[curve].keys())
        xunits = curvekeys[0]
        yunits = curvekeys[1]
        x = np.array(self.data[curve][xunits])
        y = np.array(self.data[curve][yunits])

        if self.counter == 1:
            self.ax2 = self.ax1.twinx()
            self.ax2.plot(x, y, color=color, lw=lw, label=curve)
            self.ax2.tick_params(axis='y', labelsize=8, colors=color)
            if ylim:
                self.ax2.set_ylim(ylim)
            else:
                self.ax2.set_ylim(bottom=0)
            if ylabel:
                self.ax2.set_ylabel(ylabel, color=color, fontsize=10)
            self.counter += 1
        else:
            new_ax = self.ax1.twinx()
            new_ax.spines['right'].set_position(('outward', 45 * (self.counter - 1)))
            new_ax.plot(x, y, color=color, lw=lw, label=curve)
            new_ax.tick_params(axis='y', labelsize=8, colors=color)
            if ylim:
                new_ax.set_ylim(ylim)
            else:
                new_ax.set_ylim(bottom=0)
            if ylabel:
                new_ax.set_ylabel(ylabel, color=color, fontsize=10)
            new_ax.set_frame_on(True)
            self.counter += 1
    
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
            plt.axvline( x = f[i], ymin = 0,  ymax = 0.05, color = 'red', 
                ls = ':' )
        for i in range(len(flabx)):
            plt.text(flabx[i], labheight, flab[i], fontsize = fontsize, ha = 'center')

    def shadeFrac(self, curve, startFrac, stopFrac, color='gray', alpha=0.5):
        try:
            fractions = self.data['Fraction']['Fraction']
            volumes = self.data['Fraction']['ml']
        except KeyError:
            raise KeyError('Fraction data does not seem to be present')

        fractions = [x.strip("T\"") for x in fractions]

        if startFrac not in fractions or stopFrac not in fractions:
            raise ValueError('Specified fractions are not in the data')

        startIndex = fractions.index(startFrac)
        stopIndex = fractions.index(stopFrac)

        startVol = volumes[startIndex]
        stopVol = volumes[stopIndex]

        curvekeys = list(self.data[curve].keys())
        xunits = curvekeys[0]
        yunits = curvekeys[1]
        x = np.array(self.data[curve][xunits])
        y = np.array(self.data[curve][yunits])

        mask = (x >= startVol) & (x <= stopVol)
        x_shaded = x[mask]
        y_shaded = y[mask]

        self.ax1.fill_between(x_shaded, y_shaded, color=color, alpha=alpha)

    def addLegend(self):
        handles_labels = [ax.get_legend_handles_labels() for ax in self.fig.get_axes()]
        handles, labels = zip(*handles_labels)
        handles = [item for sublist in handles for item in sublist]
        labels = [item for sublist in labels for item in sublist]
    
        self.ax1.legend(loc='upper center', bbox_to_anchor=(0.5, 1.12), ncol=10, fontsize=8,
                        handles=handles, labels=labels)

    def finishPlot (self):
        plt.tight_layout()
        plt.show()

    def savePlot(self, outname):
        plt.savefig(outname)


class AktaPlotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Chromatography Data Plotter")

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        window_width = 380
        window_height = 400
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()

        position_top = int(screen_height/3 - window_height/2)
        position_right = int(screen_width/4 - window_width/2)

        root.geometry(f"{window_width}x{window_height}+{position_right}+{position_top}")

        self.filename = ''
        self.data = None

        self.create_widgets() # Initialise GUI components

    def create_widgets(self):
        # Main frame for widgets
        self.frame = ttk.Frame(self.root, padding="10 10 10 10")
        self.frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Button to load data file
        self.load_button = ttk.Button(self.frame, text="Load Data File", command=self.load_file)
        self.load_button.grid(row=0, column=0, columnspan=2, pady=5)

        # Label and combobox to select curve to plot
        self.curve_label = ttk.Label(self.frame, text="Curve to Plot:")
        self.curve_label.grid(row=1, column=0, sticky=tk.W)
        self.curve_combobox = ttk.Combobox(self.frame, state="readonly")
        self.curve_combobox.grid(row=1, column=1, sticky=(tk.W, tk.E))

        # Button and canvas to select and display color
        self.color_button = ttk.Button(self.frame, text="Select Color", command=self.choose_color)
        self.color_button.grid(row=2, column=0, pady=5)
        self.color_display = tk.Canvas(self.frame, width=20, height=20, bg='black')
        self.color_display.grid(row=2, column=1, pady=5, sticky=(tk.W))

        # Label and spinbox for line width
        self.linewidth_label = ttk.Label(self.frame, text="Line Width:")
        self.linewidth_label.grid(row=3, column=0, sticky=tk.W)
        self.linewidth_spinbox = ttk.Spinbox(self.frame, from_=1, to=10)
        self.linewidth_spinbox.set(1)
        self.linewidth_spinbox.grid(row=3, column=1, sticky=(tk.W, tk.E))

        # Frame for curve buttons
        self.curve_frame = ttk.Frame(self.frame)
        self.curve_frame.grid(row=4, column=0, columnspan=2, pady=5, sticky=tk.W)        

        # Button to plot selected curve
        self.plot_button = ttk.Button(self.curve_frame, text="Plot Curve", command=self.plot_curve)
        self.plot_button.grid(row=0, column=0, padx=50)

        # Button to add another curve to the plot
        self.add_curve_button = ttk.Button(self.curve_frame, text="Add Curve", command=self.add_curve)
        self.add_curve_button.grid(row=0, column=1, padx=5)

        # Frame for checkboxes
        self.checkbox_frame = ttk.Frame(self.frame)
        self.checkbox_frame.grid(row=6, column=0, columnspan=2, pady=5, sticky=tk.W)

        # Checkbox to add fractions to the plot
        self.add_fractions_var = tk.BooleanVar(value=False)
        self.add_fractions_checkbox = ttk.Checkbutton(self.checkbox_frame, text="Add Fractions", variable=self.add_fractions_var, command=self.refresh_plot)
        self.add_fractions_checkbox.grid(row=0, column=0, padx=50)

        # Checkbox to add legend to the plot
        self.legend_checkbox_var = tk.BooleanVar(value=False)
        self.legend_checkbox = ttk.Checkbutton(self.checkbox_frame, text="Add Legend", variable=self.legend_checkbox_var, command=self.add_legend)
        self.legend_checkbox.grid(row=0, column=1, padx=5)

        # Entry fields for y-axis label and limits
        self.y_axis_label_label = ttk.Label(self.frame, text="Y-axis Label:")
        self.y_axis_label_label.grid(row=8, column=0, sticky=tk.W)
        self.y_axis_label_entry = ttk.Entry(self.frame)
        self.y_axis_label_entry.grid(row=8, column=1, sticky=(tk.W, tk.E))

        self.y_axis_limits_label = ttk.Label(self.frame, text="Y-axis Limits (min, max):")
        self.y_axis_limits_label.grid(row=9, column=0, sticky=tk.W)
        self.y_axis_limits_entry = ttk.Entry(self.frame)
        self.y_axis_limits_entry.grid(row=9, column=1, sticky=(tk.W, tk.E))

        # Entry fields for start and stop fractions
        self.start_fraction_label = ttk.Label(self.frame, text="Start Fraction:")
        self.start_fraction_label.grid(row=10, column=0, sticky=tk.W)
        self.start_fraction_entry = ttk.Entry(self.frame)
        self.start_fraction_entry.grid(row=10, column=1, sticky=(tk.W, tk.E))

        self.stop_fraction_label = ttk.Label(self.frame, text="Stop Fraction:")
        self.stop_fraction_label.grid(row=11, column=0, sticky=tk.W)
        self.stop_fraction_entry = ttk.Entry(self.frame)
        self.stop_fraction_entry.grid(row=11, column=1, sticky=(tk.W, tk.E))

        # Button to shade specified fractions in the plot
        self.shade_button = ttk.Button(self.frame, text="Shade Fractions", command=self.shade_fractions)
        self.shade_button.grid(row=12, column=0, columnspan=2, pady=5)

        # Button to save the plot to a file
        self.save_button = ttk.Button(self.frame, text="Save Plot", command=self.save_plot)
        self.save_button.grid(row=13, column=0, columnspan=2, pady=5)

        # Frame for the plot figure
        self.figure_frame = ttk.Frame(self.root)
        self.figure_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.canvas = None

    def load_file(self):
        # Open file dialog to select a data file
        self.filename = filedialog.askopenfilename(filetypes=[("Text files", "*.txt"),("ASCII files", "*.asc"), ("All files", "*.*")])
        if not self.filename:
            return
        # Load the data using AKdatafile
        self.data = AKdatafile(self.filename).genAKdict(1,2)
        self.curve_combobox['values'] = list(self.data.keys())
        self.curve_combobox.current(0)
        print(f"Loaded data from {self.filename}")

    def choose_color(self):
        # Open a color chooser dialog and set the selected color
        color_code = colorchooser.askcolor(title="Choose Color")
        if color_code:
            self.color_display.config(bg=color_code[1])

    def plot_curve(self):
        if not self.data:
            return

        # Get selected curve and color
        curve = self.curve_combobox.get()
        color = self.color_display.cget("bg")
        linewidth = float(self.linewidth_spinbox.get())
        ylabel = self.y_axis_label_entry.get()

        # Create a plot
        self.chrom_data = chromData(self.data)
        self.chrom_data.plotCurve(curve, color=color, ylabel=ylabel, lw=linewidth)

        # Add fractions if the checkbox is selected
        if self.add_fractions_var.get():
            self.chrom_data.addFractions()

        self.display_plot()

    def add_curve(self):
        if not self.data or not hasattr(self, 'chrom_data'):
            return

        # Get selected curve, color and other properties
        curve = self.curve_combobox.get()
        color = self.color_display.cget("bg")
        linewidth = float(self.linewidth_spinbox.get())
        ylabel = self.y_axis_label_entry.get()

        y_limits = self.y_axis_limits_entry.get()
        ylim = None
        if y_limits:
            try:
                ylim = tuple(map(float, y_limits.split(',')))
            except ValueError:
                pass

        # Add another curve to the plot
        self.chrom_data.addCurve(curve, color=color, ylim=ylim, ylabel=ylabel, lw=linewidth)
        self.display_plot()

    def shade_fractions(self):
        if not self.data or not hasattr(self, 'chrom_data'):
            return

        # Get curve and fractions to shade
        curve = self.curve_combobox.get()
        start_frac = self.start_fraction_entry.get()
        stop_frac = self.stop_fraction_entry.get()

        # Shade the specified fractions
        self.chrom_data.shadeFrac(curve, start_frac, stop_frac)
        self.display_plot()

    def add_legend(self):
        if not self.data or not hasattr(self, 'chrom_data'):
            return

        # Add legend to the plot
        self.chrom_data.addLegend()
        self.display_plot()

    def display_plot(self):
        # Destroy the existing canvas widget
        if self.canvas:
            self.canvas.get_tk_widget().destroy()

        # Create a new canvas widget to display the plot
        self.canvas = FigureCanvasTkAgg(self.chrom_data.fig, master=self.figure_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def refresh_plot(self):
        if not self.data or not hasattr(self, 'chrom_data'):
            return
        
        # Clear and refresh the plot
        self.chrom_data.fig.clear()
        self.plot_curve()
        self.add_curve()
        self.shade_fractions()
        self.add_legend()

    def save_plot(self):
        if not self.data or not hasattr(self, 'chrom_data'):
            return

        # Open a file dialog to save the plot
        filename = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")])
        if filename:
            self.chrom_data.savePlot(filename)
            print(f"Plot saved to {filename}")

    def on_closing(self):
        # Ensure script stops running when window is closed
        self.root.quit()
        self.root.destroy()

# Initialise and run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = AktaPlotApp(root)
    root.mainloop()


