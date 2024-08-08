import sys
import AKdatafile as AKdf
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QHBoxLayout, QVBoxLayout, QWidget, QDialog, QFileDialog,
    QMessageBox, QCheckBox, QLabel, QDialogButtonBox, QLineEdit
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.ticker import AutoMinorLocator

# from rich.traceback import install
# install()

plt.rcParams['pdf.fonttype'] = 42
plt.rcParams['ps.fonttype'] = 42
plt.rcParams['font.sans-serif'] = "Arial"
plt.rcParams['font.family'] = "sans-serif"

'''
To do:
- Give error rather than quitting when options are tried with no data loaded
- Sort formatting of curve checkboxes - move into new dialog?, easier to add options for color, ls etc.
- Remove first and waste fractions
- Tabs
- Add run log as annotations

'''

class AnalyseDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Analyse")

        # Create layout
        self.layout = QVBoxLayout()

        self.layout.addWidget(QLabel("Analyse"))
        self.layout.addWidget(QLabel("Functionality yet to be added"))

        # Add buttons
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.layout.addWidget(self.button_box)

        # Set the layout
        self.setLayout(self.layout)

class OptionsDialog(QDialog):
    legendToggled = pyqtSignal(bool)
    fractionLabelsToggled = pyqtSignal(bool)
    shadeFractionsRequested = pyqtSignal(int, int)
    undoShadeRequested = pyqtSignal()
    clearShadeRequested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Options")

        # Create layout
        self.layout = QVBoxLayout()

        # Create and add widgets
        self.add_fraction_labels_checkbox = QCheckBox("Add fraction labels")
        self.add_legend_checkbox = QCheckBox("Add Legend")
        self.add_legend_checkbox.setChecked(False)  # Legend off by default

        self.add_fraction_labels_checkbox.stateChanged.connect(self.toggle_fraction_labels)
        self.add_legend_checkbox.stateChanged.connect(self.toggle_legend)

        self.start_fraction_label = QLabel("Start Fraction")
        self.start_fraction_input = QLineEdit()
        self.stop_fraction_label = QLabel("Stop Fraction")
        self.stop_fraction_input = QLineEdit()
        self.shade_button = QPushButton("Shade")
        self.undo_button = QPushButton("Undo")
        self.clear_button = QPushButton("Clear")

        self.shade_button.clicked.connect(self.shade_fractions)
        self.undo_button.clicked.connect(self.undo_shade)
        self.clear_button.clicked.connect(self.clear_shade)

        options_label = QLabel("Options")
        bold_large_font = QFont()
        bold_large_font.setBold(True)
        bold_large_font.setPointSize(16)
        options_label.setFont(bold_large_font)

        shade_fractions_label = QLabel("Shade Fractions")
        bold_font = QFont()
        bold_font.setBold(True)
        shade_fractions_label.setFont(bold_font)


        # Add checkboxes to layout
        self.layout.addWidget(options_label)
        self.layout.addWidget(self.add_fraction_labels_checkbox)
        self.layout.addWidget(self.add_legend_checkbox)
        self.layout.addWidget(shade_fractions_label)
        self.layout.addWidget(self.start_fraction_label)
        self.layout.addWidget(self.start_fraction_input)
        self.layout.addWidget(self.stop_fraction_label)
        self.layout.addWidget(self.stop_fraction_input)
        self.layout.addWidget(self.shade_button)
        self.layout.addWidget(self.undo_button)
        self.layout.addWidget(self.clear_button)

        # Set the layout
        self.setLayout(self.layout)

    def toggle_legend(self):
        self.legendToggled.emit(self.add_legend_checkbox.isChecked())

    def toggle_fraction_labels(self):
        self.fractionLabelsToggled.emit(self.add_fraction_labels_checkbox.isChecked())

    def shade_fractions(self):
        try:
            start_frac = int(self.start_fraction_input.text())
            stop_frac = int(self.stop_fraction_input.text())
            self.shadeFractionsRequested.emit(start_frac, stop_frac)
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Please enter valid integer fractions.")

    def undo_shade(self):
        self.undoShadeRequested.emit()

    def clear_shade(self):
        self.clearShadeRequested.emit()

    def get_options(self):
        return {
            'Add fraction labels': self.add_fraction_labels_checkbox.isChecked(),
            'Add Legend': self.add_legend_checkbox.isChecked(),
        }

    def set_options(self, options):
        self.add_fraction_labels_checkbox.setChecked(options.get('Add fraction labels', False))
        self.add_legend_checkbox.setChecked(options.get('Add Legend', False))


class SingleMode(QDialog):
    def __init__(self, mode_name, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Single Mode")
        
        self.mode_name = mode_name
        self.loaded_file = None
        self.data = None
        self.colors = ['r', 'g', 'b', 'c', 'm']
        self.show_legend = False
        self.show_fraction_labels = False
        self.options_state = {
            'Add fraction labels': False,
            'Add Legend': False
        }

        self.shaded_regions = []
        self.show_shaded_fractions = False

        # Create layouts
        self.main_layout = QVBoxLayout()
        self.button_layout = QHBoxLayout()
        self.side_layout = QHBoxLayout()
        self.checkbox_layout = QVBoxLayout()

        # Create buttons
        self.load_data_button = QPushButton("Load data")
        self.clear_data_button = QPushButton("Clear data")
        self.save_plot_button = QPushButton("Save plot")
        self.options_button = QPushButton("Options")
        self.analyse_button = QPushButton("Analyse")
        self.back_button = QPushButton("Back")

        # Add buttons to the button layout
        self.button_layout.addWidget(self.load_data_button)
        self.button_layout.addWidget(self.clear_data_button)
        self.button_layout.addWidget(self.save_plot_button)
        self.button_layout.addWidget(self.options_button)
        self.button_layout.addWidget(self.analyse_button)
        self.button_layout.addWidget(self.back_button)

        # Create a matplotlib figure and canvas
        self.figure = plt.figure(figsize=(14,7))
        self.canvas = FigureCanvas(self.figure)

        # Add the canvas and checkbox layout to the side layout
        self.side_layout.addLayout(self.checkbox_layout)
        self.side_layout.addWidget(self.canvas)

        # Add the button layout and side layout to the main layout
        self.main_layout.addLayout(self.button_layout)
        self.main_layout.addLayout(self.side_layout)

        # Set the layout to the dialog
        self.setLayout(self.main_layout)

        # Connect the buttons to their respective methods
        self.load_data_button.clicked.connect(self.load_data)
        self.clear_data_button.clicked.connect(self.clear_data)
        self.save_plot_button.clicked.connect(self.save_plot)
        self.options_button.clicked.connect(self.open_options_dialog)
        self.analyse_button.clicked.connect(self.open_analyse_dialog)
        self.back_button.clicked.connect(self.close_dialog)

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
            "Text Files (*.txt);;ASC Files (*.asc);;CSV Files (*.csv);;All Files (*)", 
            options=options
        )
        if file_name:
            print(f"File loaded: {file_name}")
            self.loaded_file = file_name
            self.data = AKdf.AKdatafile(file_name).genAKdict(1, 2)
            self.create_checkboxes()
            self.update_plot()

    def create_checkboxes(self):
        # Remove old checkboxes
        for i in reversed(range(self.checkbox_layout.count())):
            widget = self.checkbox_layout.itemAt(i).widget()
            if widget and widget not in [self.load_data_button, self.clear_data_button, self.save_plot_button, self.back_button]:
                widget.setParent(None)

        # Create new checkboxes for the curves
        self.checkboxes = {}
        self.checkbox_layout.addWidget(QLabel("Curves"))
        for curve in self.data.keys():
            if curve != 'UV':  # Exclude 'UV' since it's already plotted
                checkbox = QCheckBox(curve)
                checkbox.setChecked(False)  # Default to unchecked
                checkbox.stateChanged.connect(self.update_plot)
                self.checkbox_layout.addWidget(checkbox)
                self.checkboxes[curve] = checkbox

        # Update the plot with current checkbox states
        self.update_plot()

    def update_plot(self):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        self.fraction_labels = []
        self.ax1 = ax

        handles = []
        labels = []

        # Always plot UV
        if 'UV' in self.data:
            curve = 'UV'
            curvekeys = list(self.data[curve].keys())
            xunits = curvekeys[0]
            yunits = curvekeys[1]
            x = np.array(self.data[curve][xunits])
            y = np.array(self.data[curve][yunits])
            uv_line, = ax.plot(x, y, label='UV', color='k')
            ax.set_xlim(left=0, right=max(self.data[curve][xunits]))
            handles.append(uv_line)
            labels.append('UV')

        # Plot selected curves
        y_axes = [ax]

        for i, (curve, checkbox) in enumerate(self.checkboxes.items()):
            if checkbox.isChecked() and curve in self.data:
                color = self.colors[i % len(self.colors)]
                curvekeys = list(self.data[curve].keys())
                xunits = curvekeys[0]
                yunits = curvekeys[1]
                x = np.array(self.data[curve][xunits])
                y = np.array(self.data[curve][yunits])

                if len(y_axes) == 1:
                    new_ax = ax.twinx()
                    y_axes.append(new_ax)
                elif len(y_axes) > 1:
                    new_ax = ax.twinx()
                    new_ax.spines['right'].set_position(('outward', 40 * len(y_axes)))
                    y_axes.append(new_ax)

                line, = new_ax.plot(x, y, label=curve, color=color)
                new_ax.set_ylabel(curve, color=color)
                new_ax.tick_params(axis='y', labelcolor=color)

                handles.append(line)
                labels.append(curve)

        ax.set_xlabel('Volume (mL)')
        ax.set_ylabel('UV (mAU)')

        if self.show_legend:
            ax.legend(
                loc='upper center', bbox_to_anchor=(0.5, 1.12), ncol=10, fontsize=8,
                handles=handles, labels=labels
            )

        if self.show_fraction_labels:
            self.add_fractions()

        if self.show_shaded_fractions:
            for start_frac, stop_frac in self.shaded_regions:
                self._shade_fractions(start_frac, stop_frac)

      
        plt.tight_layout()

        self.canvas.draw()

    def add_fractions(self, stript=True, fontsize=6, labheight=5):
        flabx = []
        try:
            f = self.data['Fraction']['ml']
            flab = self.data['Fraction']['Fraction']
        except KeyError:
            raise KeyError('Fraction data does not seem to be present')
        
        for i in range(len(flab) - 1):
            flabx.append((f[i] + f[i+1]) / 2)

        if stript:
            flab = [x.strip("T\"") for x in flab]
        else:
            pass

        for i in range(len(f)):
            if flab[i] == "Waste":
                continue

            line = self.ax1.axvline(x=f[i], ymin=0, ymax=0.05, color='red', ls=':')
            self.fraction_labels.append(line)

        for i in range(len(flabx)):
            if flab[i] == "Waste":
                continue

            label = self.ax1.text(flabx[i], labheight, flab[i], fontsize=fontsize, ha='center')
            self.fraction_labels.append(label)

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
                self.figure.clear()
                for i in reversed(range(self.checkbox_layout.count())):
                    widget = self.checkbox_layout.itemAt(i).widget()
                    if widget and widget not in [self.load_data_button, self.clear_data_button, self.save_plot_button, self.back_button]:
                        widget.setParent(None)
                print("All data cleared.")
                self.canvas.draw()
        else:
            print("Data clearing canceled.")

    def save_plot(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(
            self, "Save Plot", "", 
            "PDF Files (*pdf);;PNG Files (*.png);;JPEG Files (*.jpg);;All Files (*)", 
            options=options
        )
        if file_name:
            self.figure.savefig(file_name)
            QMessageBox.information(self, "Save Plot", "Plot saved successfully!")

    def close_dialog(self):
        self.close()
        if self.parent():
            self.parent().show()

    def open_options_dialog(self):
        options_dialog = OptionsDialog(self)
        options_dialog.set_options(self.options_state)
        options_dialog.legendToggled.connect(self.set_legend_visibility)
        options_dialog.fractionLabelsToggled.connect(self.set_fraction_labels_visibility)
        options_dialog.shadeFractionsRequested.connect(self.set_shaded_fractions_visibility)
        options_dialog.undoShadeRequested.connect(self.undo_shade)
        options_dialog.clearShadeRequested.connect(self.clear_shaded_regions)
        options_dialog.show()
        self.options_state = options_dialog.get_options()

    def set_legend_visibility(self, visible):
        self.show_legend = visible
        self.update_plot()

    def set_fraction_labels_visibility(self, visible):
        self.show_fraction_labels = visible
        self.update_plot()

    def set_shaded_fractions_visibility(self, start_frac, stop_frac, color='grey', alpha=0.5):
        try:
            # Retrieve fraction data
            fractions = self.data['Fraction']['Fraction']
            volumes = self.data['Fraction']['ml']
        except KeyError:
            QMessageBox.warning(self, "Error", "Fraction data does not seem to be present.")
            return

        # Clean and convert fraction numbers to integers
        fractions = [int(x.strip("T\"")) for x in fractions if x.strip("T\"").isdigit()]

        # Check if specified fractions exist in the data
        if start_frac not in fractions or stop_frac not in fractions:
            QMessageBox.warning(self, "Error", "Specified fractions are not in the data.")
            return

        # Get the indices of the start and stop fractions
        start_index = fractions.index(start_frac)
        stop_index = fractions.index(stop_frac)

        # Get the corresponding volume ranges
        start_vol = volumes[start_index]
        stop_vol = volumes[stop_index]

        # Save the shaded region for potential future use
        self.shaded_regions.append((start_frac, stop_frac))  # Save the fraction range
        self.show_shaded_fractions = True

        # Apply shading
        self._shade_fractions(start_frac, stop_frac, color=color, alpha=alpha)

    def _shade_fractions(self, start_frac, stop_frac, color='grey', alpha=0.5):
        # Retrieve fraction data
        fractions = self.data['Fraction']['Fraction']
        volumes = self.data['Fraction']['ml']
        
        # Convert fraction numbers to integers
        fractions = [int(x.strip("T\"")) for x in fractions if x.strip("T\"").isdigit()]

        # Get the indices of the start and stop fractions
        start_index = fractions.index(start_frac)
        stop_index = fractions.index(stop_frac)

        # Get the corresponding volume ranges
        start_vol = volumes[start_index]
        stop_vol = volumes[stop_index]

        # Shade the area under the curve between the start and stop volumes
        xdata, ydata = self.ax1.lines[0].get_data()  # Assuming the UV curve is the first plotted line
        mask = (xdata >= start_vol) & (xdata <= stop_vol)
        self.ax1.fill_between(xdata[mask], ydata[mask], color=color, alpha=alpha)
        self.canvas.draw()

    def undo_shade(self):
        if self.shaded_regions:
            self.shaded_regions.pop()
            self.update_plot()

    def clear_shaded_regions(self):
        self.shaded_regions.clear()
        self.update_plot()

    def open_analyse_dialog(self):
        analyse_dialog = AnalyseDialog(self)
        analyse_dialog.show()


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
        self.single_mode_dialog = SingleMode("Single Mode", self)
        self.hide()
        self.single_mode_dialog.show()

    def overlay_mode(self):
        self.overlay_mode_dialog = OverlayMode(self)
        self.hide()
        self.overlay_mode_dialog.exec_()


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
