'''
ChromaPlot Version 1.0.0
Authors: Billy Hobbs and Felipe Ossa
© 2024 Billy Hobbs. All rights reserved.
'''

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QHBoxLayout, QVBoxLayout, QWidget, QDialog, QFileDialog,
    QMessageBox, QCheckBox, QLabel, QDialogButtonBox, QLineEdit, QColorDialog, QComboBox, QDoubleSpinBox,
    QButtonGroup, QRadioButton, QFrame, QSlider, QTextEdit, QSizePolicy, QGridLayout
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator

import numpy as np
import os
import AKdatafile as AKdf
from help_dialogs import MainHelpDialog


class OverlayMode(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Overlay Mode")

        self.loaded_datasets = {}  
        self.plot_settings = {}  

        self.xmin = None
        self.xmax = None
        self.ymin = None
        self.ymax = None

        self.y_label = "UV (mAU)"

        self.show_legend = False
        self.legend_location = 'best'

        self.select_curves_dialog = None
        self.options_dialog = None

        # Create layouts
        self.main_layout = QVBoxLayout()
        self.button_layout = QHBoxLayout()
        self.side_layout = QHBoxLayout()

        # Create buttons
        self.load_data_button = QPushButton("Load data")
        self.clear_data_button = QPushButton("Clear data")
        self.save_plot_button = QPushButton("Save plot")
        self.options_button = QPushButton("Display options")
        self.select_curves_button = QPushButton("Select curves")
        self.back_button = QPushButton("Back")
        self.help_button = QPushButton("Help")

        # Add buttons to the button layout
        self.button_layout.addWidget(self.load_data_button)
        self.button_layout.addWidget(self.clear_data_button)
        self.button_layout.addWidget(self.save_plot_button)
        self.button_layout.addWidget(self.options_button)
        self.button_layout.addWidget(self.select_curves_button)
        self.button_layout.addWidget(self.back_button)
        self.button_layout.addWidget(self.help_button)

        # Create a matplotlib figure and canvas
        self.figure = plt.figure(figsize=(7, 3.5))
        self.canvas = FigureCanvas(self.figure)

        frame = QFrame()
        frame.setObjectName("plotFrame")
        
        plot_layout = QVBoxLayout()
        plot_layout.setContentsMargins(0,0,0,0)
        plot_layout.setSpacing(0)
        plot_layout.addWidget(self.canvas)
        frame.setLayout(plot_layout)

        self.side_layout.addWidget(frame)

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
        self.select_curves_button.clicked.connect(self.open_select_curves_dialog)
        self.back_button.clicked.connect(self.close_dialog)
        self.help_button.clicked.connect(self.open_help_dialog)

    def is_data_loaded(self):
        if self.data is None:
            QMessageBox.warning(self, "No Data Loaded", "Please load data before using this option.")
            return False
        return True

    def load_data(self):
    # Load data and open select curves dialog
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_names, _ = QFileDialog.getOpenFileNames(
            self, "Load Data Files", "",
            "Text Files (*.txt);;ASC Files (*.asc);;CSV Files (*.csv);;All Files (*)",
            options=options
        )
        if file_names:
            for file_name in file_names:
                print(f"File loaded: {file_name}")
                dataset_name = os.path.basename(file_name)
                data = AKdf.AKdatafile(file_name).genAKdict(1, 2)

                # Store dataset and default plot settings
                self.loaded_datasets[dataset_name] = data
                self.plot_settings[dataset_name] = {
                    'linestyle': '-',
                    'linewidth': 1.5,
                    'color': 'black',
                    'label': dataset_name
                }

            # Open the Select Curves dialog after loading all datasets
            self.open_select_curves_dialog()

            # Update the plot with the new datasets
            self.update_plot()

    def open_select_curves_dialog(self):
        if not self.loaded_datasets:
            QMessageBox.warning(self, "No Data Loaded", "Please load data before using this option")
            return
        if self.select_curves_dialog is not None:
            self.select_curves_dialog.close()

        self.select_curves_dialog = OverlaySelectCurvesDialog(self.loaded_datasets, self.plot_settings, self)
        self.select_curves_dialog.move(self.x() + 750, self.y() + 50)
        self.select_curves_dialog.show()

        # Connect the signal for updating the plot with selected curves
        self.select_curves_dialog.curveOptionsChanged.connect(self.update_plot)

    def open_options_dialog(self):
        if not self.loaded_datasets:
            QMessageBox.warning(self, "No Data Loaded", "Please load data before using this option")
            return
        if self.options_dialog is not None:
            self.options_dialog.close()

        self.options_dialog = OverlayOptionsDialog(self)
        self.options_dialog.move(self.x() - 250, self.y() + 50)         
        self.options_dialog.show()

        # Connect signals for x and y limits, and legend visibility
        self.options_dialog.xLimitChanged.connect(self.set_x_limits)
        self.options_dialog.yLimitChanged.connect(self.set_y_limits)
        self.options_dialog.resetXLimits.connect(self.reset_x_limits)
        self.options_dialog.resetYLimits.connect(self.reset_y_limits)        
        self.options_dialog.legendToggled.connect(self.toggle_legend)
        self.options_dialog.legendLocationChanged.connect(self.set_legend_location)
        self.options_dialog.yLabelChanged.connect(self.set_y_label)

    def update_plot(self):
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        handles = []
        labels = []

        if self.plot_settings:
            for dataset_name, settings in self.plot_settings.items():
                data = self.loaded_datasets.get(dataset_name)
                if data:
                    curvekeys = list(data['UV'].keys())
                    x = np.array(data['UV'][curvekeys[0]])
                    y = np.array(data['UV'][curvekeys[1]])

                    line, = ax.plot(
                        x, y, label=settings['label'],
                        color=settings['color'],
                        linestyle=settings['linestyle'],
                        linewidth=settings['linewidth']
                    )
                    handles.append(line)
                    labels.append(settings['label'])

        else:
            # If no datasets are selected, just plot empty axes with the set limits
            ax.plot([], [])  # Empty plot

        if self.xmin is not None or self.xmax is not None:
            ax.set_xlim(left=self.xmin, right=self.xmax)

        if self.ymin is not None or self.ymax is not None:
            ax.set_ylim(bottom=self.ymin, top=self.ymax)

        ax.set_xlabel('Volume (mL)')
        ax.set_ylabel(self.y_label)

        if self.show_legend and handles:
            if self.legend_location == 'upper center':
                ax.legend(handles=handles, labels=labels, loc='upper center', bbox_to_anchor=(0.5, 1.12), ncol=10, fontsize=8)
            else:
                ax.legend(handles=handles, labels=labels, loc='best', fontsize=8)

        plt.tight_layout()
        self.canvas.draw()

    def set_y_label(self, label):
        if label:
            self.y_label = label
        self.update_plot()

    def set_x_limits(self, xmin, xmax):
        self.xmin = xmin
        self.xmax = xmax
        self.update_plot()

    def set_y_limits(self, ymin, ymax):
        self.ymin = ymin
        self.ymax = ymax
        self.update_plot()

    def reset_x_limits(self):
        self.xmin = None
        self.xmax = None
        self.update_plot()

    def reset_y_limits(self):
        self.ymin = None
        self.ymax = None
        self.update_plot()       

    def toggle_legend(self, visible):
        self.show_legend = visible
        self.update_plot()

    def set_legend_location(self, location):
        self.legend_location = location
        self.update_plot()

    def clear_data(self):
        if self.select_curves_dialog:
            self.select_curves_dialog.close()
        if self.options_dialog:
            self.options_dialog.close()

        self.loaded_datasets.clear()
        self.plot_settings.clear()

        self.xmin = None
        self.xmax = None
        self.ymin = None
        self.ymax = None

        self.show_legend = False

        self.figure.clear()
        self.canvas.draw()

        QMessageBox.information(self, "Data Cleared", "All data cleared.")
        print("All data and settings cleared.")

    def save_plot(self):
        if not self.is_data_loaded():
            return

        options = QFileDialog.Options()
        file_name, selected_filter = QFileDialog.getSaveFileName(
            self, "Save Plot", "", 
            "PDF Files (*.pdf);;PNG Files (*.png);;JPEG Files (*.jpg);;All Files (*)", 
            options=options
        )

        if file_name:
            # Determine the correct file extension based on the selected filter
            if selected_filter == "PDF Files (*.pdf)":
                extension = ".pdf"
            elif selected_filter == "PNG Files (*.png)":
                extension = ".png"
            elif selected_filter == "JPEG Files (*.jpg)":
                extension = ".jpg"
            else:
                extension = ""

            # If the file name does not already end with the correct extension, append it
            if not file_name.lower().endswith(extension):
                file_name += extension

            # Save the figure using the determined file name and extension
            self.figure.savefig(file_name)

            QMessageBox.information(self, "Save Plot", "Plot saved successfully!")

    def close_dialog(self):
        if self.select_curves_dialog:
            self.select_curves_dialog.close()
        if self.options_dialog:
            self.options_dialog.close()

        self.close()
        if self.parent():
            self.parent().show()

    def open_help_dialog(self):
        self.help_dialog = MainHelpDialog(self)

        self.help_dialog.show()


class OverlaySelectCurvesDialog(QDialog):
    curveOptionsChanged = pyqtSignal()

    def __init__(self, datasets, plot_settings, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Curves")

        self.datasets = datasets
        self.plot_settings = plot_settings

        self.grid_layout = QGridLayout()

        self.current_row = 0

        for dataset_name in self.datasets.keys():
            self.setup_curve_controls(dataset_name)

        self.setLayout(self.grid_layout)

        self.update_controls()

    def setup_curve_controls(self, dataset_name):
        settings = self.plot_settings.get(dataset_name, {
            'linestyle': '-',
            'linewidth': 1.5,
            'label': dataset_name,
            'color': 'black'
        })

        # Checkbox
        checkbox = QCheckBox(dataset_name)
        checkbox.setChecked(dataset_name in self.plot_settings)
        checkbox.stateChanged.connect(lambda state, name=dataset_name: self.handle_checkbox_change(name, state))
        self.grid_layout.addWidget(checkbox, self.current_row, 0)

        # Add linestyle options
        linestyle_combo = QComboBox()
        linestyle_combo.addItems(['-', '--', '-.', ':'])
        linestyle_combo.setCurrentIndex(['-', '--', '-.', ':'].index(settings.get('linestyle', '-')))
        linestyle_combo.currentIndexChanged.connect(lambda index: self.handle_linestyle_change(dataset_name, index))
        self.grid_layout.addWidget(linestyle_combo, self.current_row, 1)

        # Add linewidth options
        linewidth_box = QDoubleSpinBox()
        linewidth_box.setRange(0.5, 5.0)
        linewidth_box.setSingleStep(0.5)
        linewidth_box.setValue(settings.get('linewidth', 1.5))
        linewidth_box.valueChanged.connect(lambda value: self.handle_linewidth_change(dataset_name, value))
        self.grid_layout.addWidget(linewidth_box, self.current_row, 2)

        # Add label input for dataset
        ylabel_edit = QLineEdit(settings.get('label', dataset_name))
        ylabel_edit.setPlaceholderText("Legend Label")
        ylabel_edit.editingFinished.connect(lambda: self.handle_label_change(dataset_name, ylabel_edit.text()))
        self.grid_layout.addWidget(ylabel_edit, self.current_row, 3)

        # Add colour picker button
        color_button = QPushButton("Color")
        color_button.clicked.connect(lambda: self.handle_color_change(dataset_name))
        self.grid_layout.addWidget(color_button, self.current_row, 4)

        self.current_row += 1

    def handle_checkbox_change(self, dataset_name, state):
        if state == Qt.Checked:
            if dataset_name not in self.plot_settings:
                self.plot_settings[dataset_name] = {
                    'linestyle': '-',
                    'linewidth': 1.5,
                    'label': dataset_name,
                    'color': 'black'
                }
        else:
            if dataset_name in self.plot_settings:
                del self.plot_settings[dataset_name]

        self.curveOptionsChanged.emit()

    def update_controls(self):
        """Update dialog controls based on current settings."""
        for dataset_name, settings in self.plot_settings.items():
            checkbox = self.findChild(QCheckBox, dataset_name)
            linestyle_combo = self.findChild(QComboBox, dataset_name + '_linestyle')
            linewidth_box = self.findChild(QDoubleSpinBox, dataset_name + '_linewidth')
            ylabel_edit = self.findChild(QLineEdit, dataset_name + '_ylabel')

            if checkbox and dataset_name in self.datasets:
                checkbox.setChecked(True)

            if linestyle_combo:
                linestyle_combo.setCurrentIndex(['-', '--', '-.', ':'].index(settings.get('linestyle', '-')))

            if linewidth_box:
                linewidth_box.setValue(settings.get('linewidth', 1.5))

            if ylabel_edit:
                ylabel_edit.setText(settings.get('label', dataset_name))

    def update_curve_options(self, state):
        self.curveOptionsChanged.emit()

    def handle_linestyle_change(self, dataset_name, index):
        if dataset_name in self.plot_settings:
            self.plot_settings[dataset_name]['linestyle'] = ['-', '--', '-.', ':'][index]
            self.curveOptionsChanged.emit()

    def handle_linewidth_change(self, dataset_name, value):
        if dataset_name in self.plot_settings:
            self.plot_settings[dataset_name]['linewidth'] = value
            self.curveOptionsChanged.emit()

    def handle_label_change(self, dataset_name, label):
        if dataset_name in self.plot_settings:
            self.plot_settings[dataset_name]['label'] = label
            self.curveOptionsChanged.emit()

    def handle_color_change(self, dataset_name):
        if dataset_name in self.plot_settings:
            color = QColorDialog.getColor(Qt.black, self, "Select Color for " + dataset_name)
            if color.isValid():
                self.plot_settings[dataset_name]['color'] = color.name()
                self.curveOptionsChanged.emit()

    def clear_curve_data(self, dataset_name):
        del self.datasets[dataset_name]
        del self.plot_settings[dataset_name]
        self.update_curve_options(None)


class OverlayOptionsDialog(QDialog):
    legendToggled = pyqtSignal(bool)
    legendLocationChanged = pyqtSignal(str)
    yLabelChanged = pyqtSignal(str)
    xLimitChanged = pyqtSignal(float, float)
    yLimitChanged = pyqtSignal(float, float)
    resetXLimits = pyqtSignal()
    resetYLimits = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Options")

        self.layout = QVBoxLayout()

        options_label = QLabel("Options")
        options_label.setFont(self._create_bold_font(16))
        self.layout.addWidget(options_label)

        self.add_legend_checkbox = QCheckBox("Add Legend")
        self.add_legend_checkbox.setChecked(parent.show_legend)
        self.add_legend_checkbox.stateChanged.connect(self.toggle_legend)

        # Legend location radio buttons
        self.legend_location_group = QButtonGroup(self)
        self.legend_above_radio = QRadioButton("Above Plot")
        self.legend_best_radio = QRadioButton("Best Location")
        if parent.legend_location == 'best':
            self.legend_best_radio.setChecked(True)
        else:
            self.legend_above_radio.setChecked(True)

        self.legend_location_group.addButton(self.legend_above_radio)
        self.legend_location_group.addButton(self.legend_best_radio)

        self.legend_above_radio.toggled.connect(self.update_legend_location)

        legend_layout = QHBoxLayout()
        legend_layout.addWidget(self.add_legend_checkbox)
        legend_layout.addWidget(self.legend_above_radio)
        legend_layout.addWidget(self.legend_best_radio)

        self.layout.addLayout(legend_layout)

        limits_label = QLabel("Define Limits")
        limits_label.setFont(self._create_bold_font(12))

        # X-axis inputs and buttons
        x_axis_input_layout = QHBoxLayout()
        self.xmin_input = QLineEdit()
        self.xmax_input = QLineEdit()
        self.xmin_input.setPlaceholderText("Min X")
        self.xmax_input.setPlaceholderText("Max X")

        x_axis_input_layout.addWidget(self.xmin_input)
        x_axis_input_layout.addWidget(self.xmax_input)

        x_axis_button_layout = QHBoxLayout()
        self.apply_x_button = QPushButton("Apply")
        self.apply_x_button.clicked.connect(self.apply_x_limits)
        self.reset_x_button = QPushButton("Reset")
        self.reset_x_button.clicked.connect(self.reset_x_limits)

        x_axis_button_layout.addWidget(self.apply_x_button)
        x_axis_button_layout.addWidget(self.reset_x_button)

        # Y-axis inputs and buttons
        y_axis_input_layout = QHBoxLayout()
        self.ymin_input = QLineEdit()
        self.ymax_input = QLineEdit()
        self.ymin_input.setPlaceholderText("Min Y")
        self.ymax_input.setPlaceholderText("Max Y")

        y_axis_input_layout.addWidget(self.ymin_input)
        y_axis_input_layout.addWidget(self.ymax_input)

        y_axis_button_layout = QHBoxLayout()
        self.apply_y_button = QPushButton("Apply")
        self.apply_y_button.clicked.connect(self.apply_y_limits)
        self.reset_y_button = QPushButton("Reset")
        self.reset_y_button.clicked.connect(self.reset_y_limits)

        y_axis_button_layout.addWidget(self.apply_y_button)
        y_axis_button_layout.addWidget(self.reset_y_button)

        # Custom Y-Label input
        ylabel_label = QLabel("Y-axis label:")
        self.ylabel_input = QLineEdit()
        self.ylabel_input.setPlaceholderText("UV (mAU)")
        self.ylabel_input.setText(self.parent().y_label)  # Initialize with the current label
        self.ylabel_input.editingFinished.connect(self.apply_y_label)

        # Add widgets to the main layout
        self.layout.addWidget(ylabel_label)
        self.layout.addWidget(self.ylabel_input)

        self.layout.addWidget(limits_label)

        self.layout.addWidget(QLabel("X-axis limits:"))
        self.layout.addLayout(x_axis_input_layout)
        self.layout.addLayout(x_axis_button_layout)

        self.layout.addWidget(QLabel("Y-axis limits:"))
        self.layout.addLayout(y_axis_input_layout)
        self.layout.addLayout(y_axis_button_layout)

        self.setLayout(self.layout)

        self.update_controls()

    def _create_bold_font(self, size):
        font = QFont()
        font.setBold(True)
        font.setPointSize(size)
        return font

    def update_controls(self):
        """Update dialog controls based on current settings."""
        self.add_legend_checkbox.setChecked(self.parent().show_legend)
        if self.parent().legend_location == 'best':
            self.legend_best_radio.setChecked(True)
        else:
            self.legend_above_radio.setChecked(True)
        self.xmin_input.setText(str(self.parent().xmin) if self.parent().xmin is not None else '')
        self.xmax_input.setText(str(self.parent().xmax) if self.parent().xmax is not None else '')
        self.ymin_input.setText(str(self.parent().ymin) if self.parent().ymin is not None else '')
        self.ymax_input.setText(str(self.parent().ymax) if self.parent().ymax is not None else '')

    def toggle_legend(self, state):
        self.legendToggled.emit(state == Qt.Checked)

    def update_legend_location(self):
        if self.legend_above_radio.isChecked():
            self.legendLocationChanged.emit('upper center')
        else:
            self.legendLocationChanged.emit('best')

    def apply_x_limits(self):
        try:
            xmin = float(self.xmin_input.text())
            xmax = float(self.xmax_input.text())
            self.xLimitChanged.emit(xmin, xmax)
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Please enter valid numerical values for X-axis limits.")

    def apply_y_limits(self):
        try:
            ymin = float(self.ymin_input.text())
            ymax = float(self.ymax_input.text())
            self.yLimitChanged.emit(ymin, ymax)
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Please enter valid numerical values for Y-axis limits.")

    def apply_y_label(self):
        ylabel = self.ylabel_input.text().strip()
        self.yLabelChanged.emit(ylabel)

    def reset_x_limits(self):
        self.resetXLimits.emit()

    def reset_y_limits(self):
        self.resetYLimits.emit()

