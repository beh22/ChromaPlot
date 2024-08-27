'''
ChromaPlot Version 1.0.0
Authors: Billy Hobbs and Felipe Ossa
© 2024 Billy Hobbs. All rights reserved.
'''

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QHBoxLayout, QVBoxLayout, QWidget, QDialog, QFileDialog,
    QMessageBox, QCheckBox, QLabel, QDialogButtonBox, QLineEdit, QColorDialog, QComboBox, QDoubleSpinBox,
    QButtonGroup, QRadioButton, QFrame, QSlider, QTextEdit, QSizePolicy, QGridLayout, QTabWidget
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator

import numpy as np
import AKdatafile as AKdf

from help_dialogs import MainHelpDialog


class SingleMode(QDialog):
    def __init__(self, mode_name, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Single Mode")
        
        self.mode_name = mode_name
        self.loaded_file = None
        self.data = None
        self.show_legend = False
        self.show_fraction_labels = False
        self.legend_location = 'upper center'

        self.colors = ['r', 'g', 'b', 'c', 'm']

        self.shaded_regions = []
        self.show_shaded_fractions = False
        self.selected_curves = {'UV': {'linestyle': '-', 'linewidth': 1.5, 'color': 'black', 'ylabel': 'UV (mAU)', 'label': 'UV'}}
        
        self.select_curves_dialog = None
        self.options_dialog = None

        self.xmin = None
        self.xmax = None
        self.ymin = None
        self.ymax = None

        self.marker_active = False
        self.marker_position = None

        # Create layouts
        self.main_layout = QVBoxLayout()
        self.button_layout = QHBoxLayout()
        self.side_layout = QHBoxLayout()
        self.checkbox_layout = QVBoxLayout()

        # Create buttons
        self.load_data_button = QPushButton("Load data")
        self.clear_data_button = QPushButton("Clear data")
        self.save_plot_button = QPushButton("Save plot")
        self.options_button = QPushButton("Display options")
        self.select_curves_button = QPushButton("Select curves")
        self.analyse_button = QPushButton("Analyse")
        self.back_button = QPushButton("Back")
        self.help_button = QPushButton("Help")

        # Add buttons to the button layout
        self.button_layout.addWidget(self.load_data_button)
        self.button_layout.addWidget(self.clear_data_button)
        self.button_layout.addWidget(self.save_plot_button)
        self.button_layout.addWidget(self.options_button)
        self.button_layout.addWidget(self.select_curves_button)
        self.button_layout.addWidget(self.analyse_button)
        self.button_layout.addWidget(self.back_button)
        self.button_layout.addWidget(self.help_button)

        # Create a matplotlib figure and canvas
        self.figure = plt.figure(figsize=(7,3.5))
        self.canvas = FigureCanvas(self.figure)

        frame = QFrame()
        frame.setObjectName("plotFrame")

        plot_layout = QVBoxLayout()
        plot_layout.setContentsMargins(0,0,0,0)
        plot_layout.setSpacing(0)
        plot_layout.addWidget(self.canvas)
        frame.setLayout(plot_layout)        

        self.side_layout.addLayout(self.checkbox_layout)
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
        self.analyse_button.clicked.connect(self.open_analyse_dialog)
        self.back_button.clicked.connect(self.close_dialog)
        self.help_button.clicked.connect(self.open_help_dialog)

    def update_marker_state(self, active, position=None):
        self.marker_active = active
        if position is not None:
            self.marker_position = position
        self.update_plot()

    def is_data_loaded(self):
        if self.data is None:
            QMessageBox.warning(self, "No Data Loaded", "Please load data before using this option.")
            return False
        return True

    def load_data(self):
        if self.loaded_file:
            reply = QMessageBox.question(
                self, 'Confirmation', 'Loading a new file will delete the current plot. Continue?',
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )
            if reply == QMessageBox.No:
                return
        
        # Clear the existing data before loading new data
        self.clear_data()

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

            # Reopen the SelectCurvesDialog with the new data
            self.open_select_curves_dialog()

            # Update the plot with the new data
            self.update_plot()

    def open_select_curves_dialog(self):
        if not self.is_data_loaded():
            return

        if self.select_curves_dialog is not None:
            self.select_curves_dialog.close()

        self.select_curves_dialog = SelectCurvesDialog(self.data.keys(), self)

        self.select_curves_dialog.move(self.x() + 750, self.y() + 50)
        self.select_curves_dialog.show()

        # Connect the signal for updating the plot with selected curves
        self.select_curves_dialog.curveOptionsChanged.connect(self.update_selected_curves)

    def update_selected_curves(self, selected_curves):
        # Clear existing non-UV curves from selected_curves
        self.selected_curves = {'UV': self.selected_curves.get('UV', {'linestyle': '-', 'linewidth': 1.5, 'color': 'black', 'ylabel': 'UV (mAU)', 'label': 'UV'})}

        # Update with new selections from the dialog
        self.selected_curves.update(selected_curves)

        # Force an update of the plot with the new curve selections
        self.update_plot()

    def update_plot(self):
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        self.fraction_labels = []
        self.ax1 = ax

        handles = []
        labels = []

        # Plot UV curve separately with its own customization options
        # if 'UV' in self.data:
        keys = [x for x in self.data.keys()]
        uv_options = self.selected_curves.get('UV', {
            'linestyle': '-', 'linewidth': 1.5, 'color': 'black', 'ylabel': 'UV (mAU)', 'label': 'UV'
        })
        curvekeys = list(self.data[keys[0]].keys())
        x = np.array(self.data[keys[0]][curvekeys[0]])
        y = np.array(self.data[keys[0]][curvekeys[1]])
        
        uv_line, = ax.plot(x, y, label=uv_options['label'], color=uv_options['color'], linestyle=uv_options['linestyle'], linewidth=uv_options['linewidth'])
        ax.set_xlim(left=0, right=max(x))
        ax.set_ylabel(uv_options['ylabel'], color=uv_options['color'])
        ax.tick_params(axis='y', labelcolor=uv_options['color'])
        minorlocator=AutoMinorLocator(5) 
        ax.xaxis.set_minor_locator(minorlocator)
        handles.append(uv_line)
        labels.append(uv_options['label'])

        # Apply custom limits if set, else use default limits
        if self.xmin is not None or self.xmax is not None:
            ax.set_xlim(left=self.xmin, right=self.xmax)
        else:
            ax.set_xlim(left=0, right=max(x))

        if self.ymin is not None or self.ymax is not None:
            ax.set_ylim(bottom=self.ymin, top=self.ymax)

        # Plot selected curves with customization options
        self.y_axes = [ax]

        for i, (curve, options) in enumerate(self.selected_curves.items()):
            if curve != 'UV' and curve in self.data:
                linestyle = options.get('linestyle', '-')
                linewidth = options.get('linewidth', 1.5)
                color = options.get('color', self.colors[i % len(self.colors)])
                ylabel = options.get('ylabel', curve)
                label = options.get('label', curve)

                curvekeys = list(self.data[curve].keys())
                x = np.array(self.data[curve][curvekeys[0]])
                y = np.array(self.data[curve][curvekeys[1]])

                if len(self.y_axes) == 1:
                    new_ax = ax.twinx()
                    self.y_axes.append(new_ax)
                elif len(self.y_axes) == 2:
                    new_ax = ax.twinx()
                    new_ax.spines['right'].set_position(('outward', 25 * len(self.y_axes)))
                    self.y_axes.append(new_ax)
                elif len(self.y_axes) > 2:
                    new_ax = ax.twinx()
                    new_ax.spines['right'].set_position(('outward', 40 * len(self.y_axes)))
                    self.y_axes.append(new_ax)                  

                try:
                    line, = new_ax.plot(x, y, label=label, color=color, linestyle=linestyle, linewidth=linewidth)
                except Exception as e:
                    print("Error plotting curve:", e)
                new_ax.set_ylabel(ylabel, color=color)
                new_ax.tick_params(axis='y', labelcolor=color)

                handles.append(line)
                labels.append(label)

        ax.set_xlabel('Volume (mL)')

        if self.show_legend:
            if self.legend_location == 'upper center':
                ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.12), ncol=10, fontsize=8, handles=handles, labels=labels)
            else:
                ax.legend(loc='best', fontsize=8, handles=handles, labels=labels)

        if self.show_fraction_labels:
            self.add_fractions()

        if self.show_shaded_fractions:
            self.add_shaded_regions()

        # Redraw the vertical marker line if it exists
        if self.marker_active and self.marker_position is not None:
            self.ax1.axvline(self.marker_position, color='red', linestyle='--')
            if hasattr(self, 'analyse_dialog') and self.analyse_dialog:
                self.analyse_dialog.update_y_values(self.marker_position)

        plt.tight_layout()
        self.canvas.draw()

    def set_legend_location(self, location):
        self.legend_location = location
        self.update_plot()

    def clear_data(self):
        if self.options_dialog:
            self.options_dialog.close()

        if self.loaded_file:
            # Reset plot-related variables to their defaults
            self.loaded_file = None
            self.data = None
            self.selected_curves = {'UV': {'linestyle': '-', 'linewidth': 1.5, 'color': 'black', 'ylabel': 'UV (mAU)', 'label': 'UV'}}
            self.shaded_regions = []
            self.show_shaded_fractions = False
            self.show_legend = False
            self.show_fraction_labels = False

            # Reset plot limits
            self.xmin = None
            self.xmax = None
            self.ymin = None
            self.ymax = None

            # Clear the plot figure
            self.figure.clear()

            # Close dialogs if they are open
            if self.select_curves_dialog is not None:
                self.select_curves_dialog.close()
                self.select_curves_dialog = None

            # Redraw the canvas
            self.canvas.draw()

            QMessageBox.information(self, "Data Cleared", "All data cleared.")

            print("All data and settings cleared.")

    def add_fractions(self, stript=True, fontsize=6, labheight=0.02):
        flabx = []
        try:
            f = self.data['Fraction']['ml']
            flab = self.data['Fraction']['Fraction']
        except KeyError:
            QMessageBox.warning(self, "Error", "Fraction data does not seem to be present.")
            # raise KeyError('Fraction data does not seem to be present')

            self.show_fraction_labels = False
            self.options_dialog.add_fraction_labels_checkbox.setChecked(False) 
            return
        
        for i in range(len(flab) - 1):
            flabx.append((f[i] + f[i+1]) / 2)

        if stript:
            flab = [x.strip("T\"") for x in flab]

        x_min, x_max = self.ax1.get_xlim()
        y_min, y_max = self.ax1.get_ylim()

        line_height = y_min + (y_max - y_min) * 0.05
        label_height = y_min + (y_max - y_min) * labheight

        for i in range(len(f)):
            if flab[i] == "Waste" or not (x_min <= f[i] <= x_max):
                continue

            start_line = self.ax1.axvline(x=f[i], ymin=0, ymax=(line_height - y_min) / (y_max - y_min), color='red', ls=':')
            self.fraction_labels.append(start_line)

            if i < len(f) - 1:
                end_line = self.ax1.axvline(x=f[i+1], ymin=0, ymax=(line_height - y_min) / (y_max - y_min), color='red', ls=':')
                self.fraction_labels.append(end_line)

        for i in range(len(flabx)):
            if flab[i] == "Waste" or not (x_min <= flabx[i] <= x_max):
                continue

            label = self.ax1.text(flabx[i], label_height, flab[i], fontsize=fontsize, ha='center', va='center')
            self.fraction_labels.append(label)

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

    def open_options_dialog(self):
        if not self.is_data_loaded():
            return
        
        if self.options_dialog:
            self.options_dialog.close()

        self.options_dialog = OptionsDialog(self)
        self.options_dialog.legendToggled.connect(self.set_legend_visibility)
        self.options_dialog.fractionLabelsToggled.connect(self.set_fraction_labels_visibility)
        self.options_dialog.shadeFractionsRequested.connect(self.set_shaded_fractions_visibility)
        self.options_dialog.undoShadeRequested.connect(self.undo_shade)
        self.options_dialog.clearShadeRequested.connect(self.clear_shaded_regions)
        self.options_dialog.xLimitChanged.connect(self.set_x_limits)
        self.options_dialog.yLimitChanged.connect(self.set_y_limits)
        self.options_dialog.resetXLimits.connect(self.reset_x_limits)
        self.options_dialog.resetYLimits.connect(self.reset_y_limits)
        self.options_dialog.legendLocationChanged.connect(self.set_legend_location)
        self.options_dialog.move(self.x() - 230, self.y() + 50) 
        self.options_dialog.show()

    def set_x_limits(self, xmin, xmax):
        if not self.is_data_loaded():
            return        
        self.xmin = xmin
        self.xmax = xmax
        self.update_plot()

    def set_y_limits(self, ymin, ymax):
        if not self.is_data_loaded():
            return        
        self.ymin = ymin
        self.ymax = ymax
        self.update_plot()

    def reset_x_limits(self):
        if not self.is_data_loaded():
            return        
        self.xmin = None
        self.xmax = None
        self.update_plot()

    def reset_y_limits(self):
        if not self.is_data_loaded():
            return
        self.ymin = None
        self.ymax = None
        self.update_plot()

    def set_legend_visibility(self, visible):
        if not self.is_data_loaded():
            return        
        self.show_legend = visible
        self.update_plot()

    def set_fraction_labels_visibility(self, visible):
        if not self.is_data_loaded():
            return        
        self.show_fraction_labels = visible
        self.update_plot()

    def set_shaded_fractions_visibility(self, start_value, stop_value, mode, color, alpha):
        if not self.is_data_loaded():
            return

        if mode == 'Fractions':
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
            if int(start_value) not in fractions or int(stop_value) not in fractions:
                QMessageBox.warning(self, "Error", "Specified fractions are not in the data.")
                return

            # Get the corresponding volume ranges
            start_index = fractions.index(int(start_value))
            stop_index = fractions.index(int(stop_value))

            start_vol = volumes[start_index]

            if stop_index + 1 < len(volumes):
                stop_vol = volumes[stop_index + 1]
            else:
                stop_vol = volumes[stop_index]

            # Store the actual volumes for shading
            self.shaded_regions.append((start_vol, stop_vol, color, alpha))
        else:
            self.shaded_regions.append((start_value, stop_value, color, alpha))

        self.show_shaded_fractions = True

        # Update the plot
        self.update_plot()

    def add_shaded_regions(self):
        if not self.is_data_loaded():
            return        
        if not self.shaded_regions:
            return

        x_lim = self.ax1.get_xlim()
        y_lim = self.ax1.get_ylim()

        for start_vol, stop_vol, color, alpha in self.shaded_regions:
            # Shade the area under the curve between the start and stop volumes
            xdata, ydata = self.ax1.lines[0].get_data() 
            mask = (xdata >= start_vol) & (xdata <= stop_vol)

            # Determine the y2 baseline, which could be the minimum y limit or a specified value
            y_min = y_lim[0]  # Use the saved minimum y-limit of the plot

            # Use fill_between with y2 set to the minimum y-limit
            self.ax1.fill_between(xdata[mask], ydata[mask], y2=y_min, color=color, alpha=alpha)

        # Restore the axis limits to what they were before shading
        self.ax1.set_xlim(x_lim)
        self.ax1.set_ylim(y_lim)

    def undo_shade(self):
        if not self.is_data_loaded():
            return        
        if self.shaded_regions:
            self.shaded_regions.pop()
            self.update_plot()

    def clear_shaded_regions(self):
        if not self.is_data_loaded():
            return        
        self.shaded_regions.clear()
        self.update_plot()

    def open_analyse_dialog(self):
        if not self.is_data_loaded():
            return        
        if hasattr(self, 'analyse_dialog') and self.analyse_dialog:
            self.analyse_dialog.close()

        self.analyse_dialog = AnalyseDialog(self)
        
        # Set the marker checkbox state based on SingleMode's marker_active attribute
        self.analyse_dialog.add_marker_checkbox.setChecked(self.marker_active)
        if self.marker_active and self.marker_position is not None:
            self.analyse_dialog.slider.setEnabled(True)
            self.analyse_dialog.slider.setValue(int(self.marker_position))

        self.analyse_dialog.move(self.x() + 250, self.y() + 450)
        self.analyse_dialog.show()

    def open_help_dialog(self):
        self.help_dialog = MainHelpDialog(self)

        self.help_dialog.show()

class SelectCurvesDialog(QDialog):
    curveOptionsChanged = pyqtSignal(dict)

    def __init__(self, curves, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Curves")

        self.curves = curves
        self.parent = parent

        self.grid_layout = QGridLayout()
        self.checkboxes = {}
        self.curve_options = {}
        excluded_curves = {'Injection', 'Run Log', 'Fraction', 'UV_CUT_TEMP@100,BASEM'}
        keys = [x for x in self.curves]

        # Initialise row counter for grid layout
        self.current_row = 0

        # Controls for UV curve
        self.setup_uv_controls()

        for curve in self.curves:
            if curve not in excluded_curves and curve != keys[0]:
                self.setup_curve_controls(curve)

        # Add grid layout to main layout
        self.main_layout = QVBoxLayout()
        self.main_layout.addLayout(self.grid_layout)
        self.setLayout(self.main_layout)

        self.update_controls()

    def setup_uv_controls(self):
        # UV checkbox and label
        uv_label = QLabel('UV:')
        self.grid_layout.addWidget(uv_label, self.current_row, 0)
        # Add linestyle options for UV
        linestyle_combo = QComboBox()
        linestyle_combo.addItems(['-', '--', '-.', ':'])
        linestyle_combo.setCurrentText(self.parent.selected_curves['UV'].get('linestyle', '-'))
        linestyle_combo.setFixedWidth(50)
        linestyle_combo.currentIndexChanged.connect(lambda index, c='UV': self.handle_linestyle_change(c)(index))
        self.grid_layout.addWidget(linestyle_combo, self.current_row, 1)

        # Add linewidth options for UV
        linewidth_box = QDoubleSpinBox()
        linewidth_box.setRange(0.5, 5.0)
        linewidth_box.setSingleStep(0.5)
        linewidth_box.setValue(self.parent.selected_curves['UV'].get('linewidth', 1.5))
        linewidth_box.setFixedWidth(50)
        linewidth_box.valueChanged.connect(lambda value, c='UV': self.handle_linewidth_change(c)(value))
        self.grid_layout.addWidget(linewidth_box, self.current_row, 2)

        # Add color picker for UV
        color_button = QPushButton("Colour")
        color_button.clicked.connect(lambda _, c='UV': self.handle_color_change(c)())
        self.grid_layout.addWidget(color_button, self.current_row, 3)

        # Add custom y-label input for UV
        ylabel_edit = QLineEdit()
        ylabel_edit.setPlaceholderText("Y label")
        ylabel_edit.setText(self.parent.selected_curves['UV'].get('ylabel', 'UV (mAU)'))
        ylabel_edit.editingFinished.connect(lambda c='UV': self.handle_ylabel_change(c, ylabel_edit.text()))
        self.grid_layout.addWidget(ylabel_edit, self.current_row, 4)

        # Add label input for UV
        label_input = QLineEdit()
        label_input.setPlaceholderText("Legend Label")
        label_input.setText(self.parent.selected_curves['UV'].get('label', 'UV'))
        label_input.editingFinished.connect(lambda: self.handle_label_change('UV', label_input.text()))
        self.grid_layout.addWidget(label_input, self.current_row, 5)

        self.current_row += 1

        # Initialize UV curve options
        self.curve_options['UV'] = self.parent.selected_curves['UV']

    def setup_curve_controls(self, curve):
        # Curve checkbox
        checkbox = QCheckBox(curve)
        checkbox.setChecked(curve in self.parent.selected_curves)
        checkbox.stateChanged.connect(self.update_curve_selection)
        self.checkboxes[curve] = checkbox
        self.grid_layout.addWidget(checkbox, self.current_row, 0)

        # Add linestyle options
        linestyle_combo = QComboBox()
        linestyle_combo.addItems(['-', '--', '-.', ':'])
        linestyle_combo.setCurrentText(self.parent.selected_curves.get(curve, {}).get('linestyle', '-'))
        linestyle_combo.setFixedWidth(50)
        linestyle_combo.currentIndexChanged.connect(lambda index, c=curve: self.handle_linestyle_change(c)(index))
        self.grid_layout.addWidget(linestyle_combo, self.current_row, 1)

        # Add linewidth options
        linewidth_box = QDoubleSpinBox()
        linewidth_box.setRange(0.5, 5.0)
        linewidth_box.setSingleStep(0.5)
        linewidth_box.setValue(self.parent.selected_curves.get(curve, {}).get('linewidth', 1.5))
        linewidth_box.setFixedWidth(50)
        linewidth_box.valueChanged.connect(lambda value, c=curve: self.handle_linewidth_change(c)(value))
        self.grid_layout.addWidget(linewidth_box, self.current_row, 2)

        # Add color picker button
        color_button = QPushButton("Colour")
        color_button.clicked.connect(lambda _, c=curve: self.handle_color_change(c)())
        self.grid_layout.addWidget(color_button, self.current_row, 3)

        # Add custom y-label input for curve
        ylabel_edit = QLineEdit()
        ylabel_edit.setPlaceholderText("Y label")
        ylabel_edit.setText(self.parent.selected_curves.get(curve, {}).get('ylabel', curve))
        ylabel_edit.editingFinished.connect(lambda c=curve: self.handle_ylabel_change(c, ylabel_edit.text()))
        self.grid_layout.addWidget(ylabel_edit, self.current_row, 4)

        # Add label input for the curve
        label_input = QLineEdit()
        label_input.setPlaceholderText("Legend Label")
        label_input.setText(self.parent.selected_curves.get(curve, {}).get('label', curve))
        label_input.editingFinished.connect(lambda: self.handle_label_change(curve, label_input.text()))
        self.grid_layout.addWidget(label_input, self.current_row, 5)

        self.current_row += 1

        self.curve_options[curve] = self.parent.selected_curves.get(curve, {
            'linestyle': '-',
            'linewidth': 1.5,
            'ylabel': curve,
            'color': 'black',
            'label': curve
        })

    def handle_linestyle_change(self, curve):
        def inner_handle_linestyle_change(index):
            combo = self.sender()
            if combo and combo.currentIndex() == index:
                self.curve_options[curve]['linestyle'] = combo.currentText()
            self.update_curve_selection(None)
        return inner_handle_linestyle_change

    def handle_linewidth_change(self, curve):
        def inner_handle_linewidth_change(value):
            spinbox = self.sender()
            if spinbox and spinbox.value() == value:
                self.curve_options[curve]['linewidth'] = value
            self.update_curve_selection(None)
        return inner_handle_linewidth_change
    
    def handle_ylabel_change(self, curve, ylabel):
        self.curve_options[curve]['ylabel'] = ylabel if ylabel else curve
        self.update_curve_selection(None)

    def handle_color_change(self, curve):
        def inner_handle_color_change():
            color = QColorDialog.getColor(Qt.black, self, "Select Color for " + curve)
            if color.isValid():
                color_name = color.name()
                self.curve_options[curve]['color'] = color_name
                self.update_curve_selection(None)
        return inner_handle_color_change
    
    def handle_label_change(self, curve, label):
        self.curve_options[curve]['label'] = label if label else curve
        self.update_curve_selection(None)

    def update_curve_selection(self, state):
        selected_curves = {}

        for curve, checkbox in self.checkboxes.items():
            if checkbox.isChecked():
                selected_curves[curve] = self.curve_options[curve]

        # Always include UV curve options
        selected_curves['UV'] = self.curve_options['UV']

        self.curveOptionsChanged.emit(selected_curves)

    def update_controls(self):
        """Update the state of controls based on the current settings in the parent."""
        for curve, options in self.parent.selected_curves.items():
            if curve in self.checkboxes:
                self.checkboxes[curve].setChecked(True)
                self.curve_options[curve] = options


class OptionsDialog(QDialog):
    legendToggled = pyqtSignal(bool)
    fractionLabelsToggled = pyqtSignal(bool)
    shadeFractionsRequested = pyqtSignal(float, float, str, str, float)
    undoShadeRequested = pyqtSignal()
    clearShadeRequested = pyqtSignal()
    xLimitChanged = pyqtSignal(float, float)
    yLimitChanged = pyqtSignal(float, float)
    resetXLimits = pyqtSignal()
    resetYLimits = pyqtSignal()
    legendLocationChanged = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Options")

        # Create main layout
        self.layout = QVBoxLayout()

        # Section: Options
        options_label = QLabel("Options")
        options_label.setFont(self._create_bold_font(16))
        self.layout.addWidget(options_label)

        self.add_fraction_labels_checkbox = QCheckBox("Add fraction labels")
        self.add_legend_checkbox = QCheckBox("Add Legend")
        self.add_legend_checkbox.setChecked(parent.show_legend)

        self.add_fraction_labels_checkbox.stateChanged.connect(self.toggle_fraction_labels)
        self.add_legend_checkbox.stateChanged.connect(self.toggle_legend)

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
        self.layout.addWidget(self.add_fraction_labels_checkbox)

        # Section: Define Limits
        limits_label = QLabel("Define Limits")
        limits_label.setFont(self._create_bold_font(12))
        self.layout.addWidget(limits_label)

        # X-axis limits
        self.layout.addWidget(QLabel("X-axis limits:"))
        x_limits_layout = QHBoxLayout()
        self.xmin_input = QLineEdit(self)
        self.xmin_input.setPlaceholderText("Min X")
        self.xmax_input = QLineEdit(self)
        self.xmax_input.setPlaceholderText("Max X")
        x_limits_layout.addWidget(self.xmin_input)
        x_limits_layout.addWidget(self.xmax_input)

        self.x_apply_button = QPushButton("Apply")
        self.x_reset_button = QPushButton("Reset")
        self.x_apply_button.clicked.connect(self.apply_x_limits)
        self.x_reset_button.clicked.connect(self.reset_x_limits)

        x_buttons_layout = QHBoxLayout()
        x_buttons_layout.addWidget(self.x_apply_button)
        x_buttons_layout.addWidget(self.x_reset_button)

        self.layout.addLayout(x_limits_layout)
        self.layout.addLayout(x_buttons_layout)

        # Y-axis limits
        self.layout.addWidget(QLabel("Y-axis limits:"))
        y_limits_layout = QHBoxLayout()
        self.ymin_input = QLineEdit(self)
        self.ymin_input.setPlaceholderText("Min Y")
        self.ymax_input = QLineEdit(self)
        self.ymax_input.setPlaceholderText("Max Y")
        y_limits_layout.addWidget(self.ymin_input)
        y_limits_layout.addWidget(self.ymax_input)

        self.y_apply_button = QPushButton("Apply")
        self.y_reset_button = QPushButton("Reset")
        self.y_apply_button.clicked.connect(self.apply_y_limits)
        self.y_reset_button.clicked.connect(self.reset_y_limits)

        y_buttons_layout = QHBoxLayout()
        y_buttons_layout.addWidget(self.y_apply_button)
        y_buttons_layout.addWidget(self.y_reset_button)

        self.layout.addLayout(y_limits_layout)
        self.layout.addLayout(y_buttons_layout)

        # Section: Shading
        shade_fractions_label = QLabel("Shading")
        shade_fractions_label.setFont(self._create_bold_font(12))
        self.layout.addWidget(shade_fractions_label)

        # Mode toggle: Fractions or Volumes
        self.shading_mode_toggle = QComboBox()
        self.shading_mode_toggle.addItems(['Fractions', 'Volumes'])
        self.shading_mode_toggle.currentIndexChanged.connect(self.update_shading_mode)
        self.layout.addWidget(self.shading_mode_toggle)

        self.start_label = QLabel("Start Fraction")
        self.start_input = QLineEdit()
        self.stop_label = QLabel("Stop Fraction")
        self.stop_input = QLineEdit()

        self.layout.addWidget(self.start_label)
        self.layout.addWidget(self.start_input)
        self.layout.addWidget(self.stop_label)
        self.layout.addWidget(self.stop_input)

        # Color picker for shading
        self.shade_color_button = QPushButton("Shade Colour")
        self.shade_color_button.clicked.connect(self.select_shade_color)
        self.shade_color = "grey"  # Default color

        # Alpha value for shading
        self.alpha_spinbox = QDoubleSpinBox()
        self.alpha_spinbox.setRange(0.0, 1.0)
        self.alpha_spinbox.setSingleStep(0.1)
        self.alpha_spinbox.setValue(0.5)  # Default alpha

        # Layout for color and alpha controls
        shade_controls_layout = QHBoxLayout()
        shade_controls_layout.addWidget(self.shade_color_button)
        shade_controls_layout.addWidget(QLabel("                Transparency:"))
        shade_controls_layout.addWidget(self.alpha_spinbox)

        self.layout.addLayout(shade_controls_layout)

        self.shade_button = QPushButton("Shade")
        self.undo_button = QPushButton("Undo")
        self.clear_button = QPushButton("Clear")

        self.shade_button.clicked.connect(self.shade_fractions)
        self.undo_button.clicked.connect(self.undo_shade)
        self.clear_button.clicked.connect(self.clear_shade)

        self.layout.addWidget(self.shade_button)
        self.layout.addWidget(self.undo_button)
        self.layout.addWidget(self.clear_button)

        # Set the layout
        self.setLayout(self.layout)

        self.update_shading_mode()

        self.update_controls()

    def _create_bold_font(self, size):
        bold_font = QFont()
        bold_font.setBold(True)
        bold_font.setPointSize(size)
        return bold_font

    def toggle_legend(self):
        self.legendToggled.emit(self.add_legend_checkbox.isChecked())

    def toggle_fraction_labels(self):
        self.fractionLabelsToggled.emit(self.add_fraction_labels_checkbox.isChecked())

    def update_legend_location(self):
        if self.legend_above_radio.isChecked():
            self.legendLocationChanged.emit('upper center')
        else:
            self.legendLocationChanged.emit('best')

    def update_shading_mode(self):
        mode = self.shading_mode_toggle.currentText()
        if mode == 'Fractions':
            self.start_label.setText("Start Fraction")
            self.stop_label.setText("Stop Fraction")
        else:
            self.start_label.setText("Start Volume")
            self.stop_label.setText("Stop Volume")

    def select_shade_color(self):
        color = QColorDialog.getColor(Qt.gray, self, "Select Shade Colour")
        if color.isValid():
            self.shade_color = color.name()

    def shade_fractions(self):
        try:
            start_value = float(self.start_input.text())
            stop_value = float(self.stop_input.text())
            mode = self.shading_mode_toggle.currentText()
            self.shadeFractionsRequested.emit(start_value, stop_value, mode, self.shade_color, self.alpha_spinbox.value())
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Please enter valid numbers for shading.")

    def undo_shade(self):
        self.undoShadeRequested.emit()

    def clear_shade(self):
        self.clearShadeRequested.emit()

    def apply_x_limits(self):
        xmin_text = self.xmin_input.text().strip()
        xmax_text = self.xmax_input.text().strip()

        if not xmin_text or not xmax_text:
            QMessageBox.warning(self, "Input Error", "Please enter both X-axis limits.")
            return

        try:
            xmin = float(xmin_text)
            xmax = float(xmax_text)
            self.xLimitChanged.emit(xmin, xmax)
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Please enter valid numbers for X-axis limits.")

    def reset_x_limits(self):
        self.xmin_input.clear()
        self.xmax_input.clear()
        self.resetXLimits.emit()

    def apply_y_limits(self):
        ymin_text = self.ymin_input.text().strip()
        ymax_text = self.ymax_input.text().strip()

        if not ymin_text or not ymax_text:
            QMessageBox.warning(self, "Input Error", "Please enter both Y-axis limits.")
            return

        try:
            ymin = float(ymin_text)
            ymax = float(ymax_text)
            self.yLimitChanged.emit(ymin, ymax)
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Please enter valid numbers for Y-axis limits.")

    def reset_y_limits(self):
        self.ymin_input.clear()
        self.ymax_input.clear()
        self.resetYLimits.emit()   

    def get_options(self):
        return {
            'Add fraction labels': self.add_fraction_labels_checkbox.isChecked(),
            'Add Legend': self.add_legend_checkbox.isChecked(),
        }

    def set_options(self, options):
        self.add_fraction_labels_checkbox.setChecked(options.get('Add fraction labels', False))
        self.add_legend_checkbox.setChecked(options.get('Add Legend', False))

    def update_controls(self):
        """Update the state of controls based on the current settings in the parent."""
        self.add_legend_checkbox.setChecked(self.parent().show_legend)
        if self.parent().legend_location == 'best':
            self.legend_best_radio.setChecked(True)
        else:
            self.legend_above_radio.setChecked(True)

        self.add_fraction_labels_checkbox.setChecked(self.parent().show_fraction_labels)

        self.xmin_input.setText(str(self.parent().xmin) if self.parent().xmin is not None else '')
        self.xmax_input.setText(str(self.parent().xmax) if self.parent().xmax is not None else '')
        self.ymin_input.setText(str(self.parent().ymin) if self.parent().ymin is not None else '')
        self.ymax_input.setText(str(self.parent().ymax) if self.parent().ymax is not None else '')


class AnalyseDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Analyse")

        self.parent = parent  # Correctly store the reference to the parent
        self.marker_line = None  # To store the vertical marker line

        # Create layout
        self.layout = QVBoxLayout()

        title = QLabel("Analyse")
        font = QFont()
        font.setBold(True)
        font.setPointSize(16)
        title.setFont(font)
        self.layout.addWidget(title)

        # Add 'Add vertical marker' checkbox
        self.add_marker_checkbox = QCheckBox("Add vertical marker")
        self.layout.addWidget(self.add_marker_checkbox)

        # Add slider
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setEnabled(False)  # Initially disabled until checkbox is checked
        self.layout.addWidget(self.slider)

        # Add text box for displaying y-values
        self.y_values_display = QTextEdit()
        self.y_values_display.setReadOnly(True)
        self.y_values_display.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.y_values_display.setFixedHeight(100) 
        self.layout.addWidget(self.y_values_display)

        # Connect signals
        self.add_marker_checkbox.stateChanged.connect(self.toggle_marker)
        self.slider.valueChanged.connect(self.update_marker_position)

        # Set the layout
        self.setLayout(self.layout)

        if self.parent.marker_active:
            self.toggle_marker(Qt.Checked)
            self.slider.setValue(int(self.parent.marker_position))

    def toggle_marker(self, state):
        if state == Qt.Checked:
            self.slider.setEnabled(True)
            if not self.marker_line:
                self.add_vertical_marker()
        else:
            self.slider.setEnabled(False)
            self.remove_vertical_marker()


    def add_vertical_marker(self):
        ax1 = self.parent.ax1

        # Retrieve current x limits from the plot, use them if xmin and xmax are None
        xmin = self.parent.xmin if self.parent.xmin is not None else ax1.get_xlim()[0]
        xmax = self.parent.xmax if self.parent.xmax is not None else ax1.get_xlim()[1]

        # Ensure xmin and xmax are valid numbers
        if xmin is None or xmax is None:
            QMessageBox.warning(self, "Error", "X-axis limits are not set properly.")
            return

        # Convert them to integers for the slider range
        self.slider.setRange(int(xmin * 100), int(xmax * 100))
        self.slider.setSingleStep(1)

        # Set the initial position of the slider to the midpoint of the range
        if self.parent.marker_position is not None:
            initial_position = self.parent.marker_position
        else:
            initial_position = (xmin + xmax) / 2  # Midpoint of the range

        self.slider.setValue(int(initial_position * 100))

        # Add the vertical marker line to the plot
        self.marker_line = ax1.axvline(initial_position, color='red', linestyle='--')

        # Update the y-values for the initial position
        self.update_y_values(initial_position)

        # Force a redraw of the canvas to display the marker immediately
        self.parent.canvas.draw()


    def remove_vertical_marker(self):
        if self.marker_line:
            self.marker_line.remove()
            self.marker_line = None
            self.y_values_display.clear()
            self.parent.canvas.draw()

    # This version works properly but is slow because the whole plot 
    # needs to be updated as the marker is moved
    # def update_marker_position(self, value):
    #     if self.marker_line:
    #         self.marker_line.set_xdata([value / 100, value / 100])
    #         self.update_y_values(value / 100)
    #         self.parent.update_marker_state(True, value / 100)  # Update the parent's marker state with the new position
    #         self.parent.canvas.draw()

    # This version is quicker, but messes up when other aspects of the plot is changed
    # Marker needs to be turned on and off again
    def update_marker_position(self, value):
        if self.marker_line:
            x_value = value / 100.0
            # Update the marker line's position without redrawing the entire canvas
            self.marker_line.set_xdata([x_value])
            self.update_y_values(x_value)
            # Only update the area where the marker is drawn instead of the entire plot
            self.parent.canvas.draw_idle()

    def update_y_values(self, x_value):
        y_values = {}

        # Iterate over each axis in the parent plot
        for ax in self.parent.y_axes:
            for curve in ax.lines:
                label = curve.get_label()
                # Filter out labels that start with an underscore
                if not label.startswith('_'):
                    x_data, y_data = curve.get_data()
                    y_value = np.interp(x_value, x_data, y_data)
                    y_values[label] = y_value

        # Prepare the text to display in the format you want
        y_values_str = f"Marker Position: {x_value:.2f} mL\n"  # Show the current volume at the top
        y_values_str += "\n".join([f"{label}: {y:.2f}" for label, y in y_values.items()])
        self.y_values_display.setText(y_values_str)
