import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QHBoxLayout, QVBoxLayout, QWidget, QDialog, QFileDialog, QMessageBox, QCheckBox
)
from PyQt5.QtCore import Qt
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
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
            with open(datafilename, 'r', encoding='UTF-8') as d:
                self.datalines = d.readlines()
        except:
            with open(datafilename, 'r', encoding='UTF-16') as d:
                self.datalines = d.readlines()

    '''Base function, splits each line by tab delimiters and removes \n 
    characters, generates a list word which is used by other functions to parse
    the data file'''
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
    def initidict (self, inlist, colno, colnoerror, indictkeys, indict, icols=2):
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
    
class ButtonWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.load_data_button = QPushButton("Load data")
        self.clear_data_button = QPushButton("Clear data")
        self.save_plot_button = QPushButton("Save plot")
        self.back_button = QPushButton("Back")

        # Create layout
        layout = QVBoxLayout()
        layout.addWidget(self.load_data_button)
        layout.addWidget(self.clear_data_button)
        layout.addWidget(self.save_plot_button)
        layout.addWidget(self.back_button)

        self.setLayout(layout)

class CheckboxWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.checkbox_layout = QVBoxLayout()
        self.setLayout(self.checkbox_layout)

    def add_checkbox(self, label):
        checkbox = QCheckBox(label)
        checkbox.setChecked(False)  # Default to unchecked
        self.checkbox_layout.addWidget(checkbox)

class CanvasWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.figure = plt.figure(figsize=(7, 3.5))
        self.canvas = FigureCanvas(self.figure)
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)

    def update_plot(self, data, checkboxes, colors):
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        # Always plot UV
        if 'UV' in data:
            curve = 'UV'
            curvekeys = list(data[curve].keys())
            xunits = curvekeys[0]
            yunits = curvekeys[1]
            x = np.array(data[curve][xunits])
            y = np.array(data[curve][yunits])
            ax.plot(x, y, label='UV', color='k')

        # Plot selected curves
        y_axes = [ax]
        for i, (curve, checkbox) in enumerate(checkboxes.items()):
            if checkbox.isChecked() and curve in data:
                color = colors[i % len(colors)]
                curvekeys = list(data[curve].keys())
                xunits = curvekeys[0]
                yunits = curvekeys[1]
                x = np.array(data[curve][xunits])
                y = np.array(data[curve][yunits])

                if len(y_axes) <= len(colors):
                    new_ax = ax.twinx()
                    new_ax.spines['right'].set_position(('outward', 0 * len(y_axes)))
                    y_axes.append(new_ax)
                else:
                    new_ax = ax.twinx()
                    new_ax.spines['right'].set_position(('outward', 60 * len(y_axes)))
                    y_axes.append(new_ax)
                    
                new_ax.plot(x, y, label=curve, color=color)
                new_ax.set_ylabel(curve, color=color)
                new_ax.tick_params(axis='y', labelcolor=color)

        ax.set_xlabel('Volume (mL)')
        ax.set_ylabel('UV (mAU)')
        ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.12), ncol=10, fontsize=8)
        plt.tight_layout()
        self.canvas.draw()

class SingleMode(QDialog):
    def __init__(self, mode_name, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Single Mode")
        
        self.mode_name = mode_name
        self.loaded_file = None
        self.data = None
        self.colors = ['r', 'g', 'b', 'c', 'm']

        # Create widgets
        self.button_widget = ButtonWidget()
        self.checkbox_widget = CheckboxWidget()
        self.canvas_widget = CanvasWidget()

        # Create layout
        self.main_layout = QHBoxLayout()
        self.main_layout.addWidget(self.checkbox_widget, 1)
        self.main_layout.addWidget(self.canvas_widget, 3)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.button_widget)
        self.layout.addLayout(self.main_layout)

        self.setLayout(self.layout)

        # Connect buttons to methods
        self.button_widget.load_data_button.clicked.connect(self.load_data)
        self.button_widget.clear_data_button.clicked.connect(self.clear_data)
        self.button_widget.save_plot_button.clicked.connect(self.save_plot)
        self.button_widget.back_button.clicked.connect(self.close_dialog)

    def load_data(self):
        if self.loaded_file:
            reply = QMessageBox.question(
                self, 'Confirmation', 'Loading a new file will delete the current plot. Continue?',
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )
            if reply == QMessageBox.No:
                return
        
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Load Data File", "", 
            "Text Files (*.txt);;CSV Files (*.csv);;ASC Files (*.asc);;All Files (*)", 
            options=options
        )
        if file_name:
            print(f"File loaded: {file_name}")
            self.loaded_file = file_name
            self.data = AKdatafile(file_name).genAKdict(1, 2)
            self.create_checkboxes()
            self.update_plot()

    def create_checkboxes(self):
        # Remove old checkboxes
        for i in reversed(range(self.checkbox_widget.checkbox_layout.count())):
            widget = self.checkbox_widget.checkbox_layout.itemAt(i).widget()
            if widget and widget not in [self.button_widget.load_data_button, self.button_widget.clear_data_button, self.button_widget.save_plot_button, self.button_widget.back_button]:
                widget.setParent(None)

        # Create new checkboxes for the curves
        self.checkboxes = {}
        for curve in self.data.keys():
            if curve != 'UV':  # Exclude 'UV' since it's already plotted
                checkbox = QCheckBox(curve)
                checkbox.setChecked(False)  # Default to unchecked
                checkbox.stateChanged.connect(self.update_plot)
                self.checkbox_widget.checkbox_layout.addWidget(checkbox)
                self.checkboxes[curve] = checkbox

        # Update the plot with current checkbox states
        self.update_plot()

    def update_plot(self):
        if self.data:
            self.canvas_widget.update_plot(self.data, self.checkboxes, self.colors)

    def clear_data(self):
        reply = QMessageBox.question(
            self, 'Clear Data',
            'Are you sure you want to clear the data?',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            if self.loaded_file:
                self.loaded_file = None
                self.data = None
                self.canvas_widget.figure.clear()
                for i in reversed(range(self.checkbox_widget.checkbox_layout.count())):
                    widget = self.checkbox_widget.checkbox_layout.itemAt(i).widget()
                    if widget and widget not in [self.button_widget.load_data_button, self.button_widget.clear_data_button, self.button_widget.save_plot_button, self.button_widget.back_button]:
                        widget.setParent(None)
                print("All data cleared.")
                self.canvas_widget.canvas.draw()
        else:
            print("Data clearing canceled.")

    def save_plot(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(
            self, "Save Plot", "", 
            "PDF Files (*.pdf);;PNG Files (*.png);;JPEG Files (*.jpg);;All Files (*)", 
            options=options
        )
        if file_name:
            self.canvas_widget.figure.savefig(file_name)
            QMessageBox.information(self, "Save Plot", "Plot saved successfully!")

    def close_dialog(self):
        self.close()
        self.parent().show()

class OverlayMode(QDialog):
    pass


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Chromaplot")

        # Create the layout
        layout = QHBoxLayout()

        # Create buttons
        self.single_mode_button = QPushButton("Single Mode")
        self.overlay_mode_button = QPushButton("Overlay Mode")

        # Add buttons to the layout
        layout.addWidget(self.single_mode_button)
        layout.addWidget(self.overlay_mode_button)

        # Set the layout to a central widget
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Connect the buttons to their respective methods
        self.single_mode_button.clicked.connect(self.single_mode)
        self.overlay_mode_button.clicked.connect(self.overlay_mode)

    def single_mode(self):
        self.mode_dialog = SingleMode(self)
        self.hide()
        self.mode_dialog.exec_()

    def overlay_mode(self):
        self.mode_dialog = OverlayMode(self)
        self.hide()
        self.mode_dialog.exec_()


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()