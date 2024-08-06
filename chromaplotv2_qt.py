import sys
from AKdatafile import *
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QHBoxLayout, QVBoxLayout, QWidget, QDialog, QFileDialog,
    QMessageBox, QCheckBox, QLabel, QDialogButtonBox
)
from PyQt5.QtCore import Qt
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.ticker import AutoMinorLocator

'''
To do:


'''

class OptionsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Options")

        # Create layout
        self.layout = QVBoxLayout()

        # Create and add widgets
        self.add_fraction_labels_checkbox = QCheckBox("Add fraction labels")
        self.add_legend_checkbox = QCheckBox("Add Legend")
        self.shade_fractions_checkbox = QCheckBox("Shade Fractions")

        # Add checkboxes to layout
        self.layout.addWidget(QLabel("Options"))
        self.layout.addWidget(self.add_fraction_labels_checkbox)
        self.layout.addWidget(self.add_legend_checkbox)
        self.layout.addWidget(self.shade_fractions_checkbox)

        # Add buttons
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.layout.addWidget(self.button_box)

        # Set the layout
        self.setLayout(self.layout)

    def get_options(self):
        return {
            'Add fraction labels': self.add_fraction_labels_checkbox.isChecked(),
            'Add Legend': self.add_legend_checkbox.isChecked(),
            'Shade Fractions': self.shade_fractions_checkbox.isChecked()
        }


class SingleMode(QDialog):
    def __init__(self, mode_name, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Single Mode")
        
        self.mode_name = mode_name
        self.loaded_file = None
        self.data = None
        self.colors = ['r', 'g', 'b', 'c', 'm']

        # Create layouts
        self.main_layout = QVBoxLayout()
        self.button_layout = QHBoxLayout()
        self.side_layout = QHBoxLayout()
        self.checkbox_layout = QVBoxLayout()
        # self.option_checkbox_layout = QVBoxLayout()

        # Create buttons
        self.load_data_button = QPushButton("Load data")
        self.clear_data_button = QPushButton("Clear data")
        self.save_plot_button = QPushButton("Save plot")
        self.back_button = QPushButton("Back")
        self.options_button = QPushButton("Options")

        # Add buttons to the button layout
        self.button_layout.addWidget(self.load_data_button)
        self.button_layout.addWidget(self.clear_data_button)
        self.button_layout.addWidget(self.save_plot_button)
        self.button_layout.addWidget(self.back_button)
        self.button_layout.addWidget(self.options_button)

        # Create a matplotlib figure and canvas
        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)

        # Arrange layouts for checkboxes
        # self.checkbox_layout.addLayout(self.option_checkbox_layout)
        # self.checkbox_layout.addLayout(self.curves_checkbox_layout)

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
        self.back_button.clicked.connect(self.close_dialog)
        self.options_button.clicked.connect(self.open_options_dialog)

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
        for i in reversed(range(self.checkbox_layout.count())):
            widget = self.checkbox_layout.itemAt(i).widget()
            if widget and widget not in [self.load_data_button, self.clear_data_button, self.save_plot_button, self.back_button]:
                widget.setParent(None)

        # Create new checkboxes for the curves
        self.checkboxes = {}
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

        # Always plot UV
        if 'UV' in self.data:
            curve = 'UV'
            curvekeys = list(self.data[curve].keys())
            xunits = curvekeys[0]
            yunits = curvekeys[1]
            x = np.array(self.data[curve][xunits])
            y = np.array(self.data[curve][yunits])
            ax.plot(x, y, label='UV', color='k')

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

                new_ax.plot(x,y, label=curve, color=color)
                new_ax.set_ylabel(curve, color=color)
                new_ax.tick_params(axis='y', labelcolor=color)

        ax.set_xlabel('Volume (mL)')
        ax.set_ylabel('UV (mAU)')
        ax.legend(
            loc='upper center', bbox_to_anchor=(0.5, 1.12), ncol=10, fontsize=8
        )
        plt.tight_layout()

        self.canvas.draw()

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
                # QMessageBox.information(self, "Clear Data", "All data has been cleared.")
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
        self.parent().show()

    def open_options_dialog(self):
        options_dialog = OptionsDialog(self)
        options_dialog.show()
        # if options_dialog.exec_() == QDialog.Accepted:
        #     options = options_dialog.get_options()
        #     print("Selected options:", options)

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
