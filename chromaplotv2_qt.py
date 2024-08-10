import sys
import AKdatafile as AKdf
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QHBoxLayout, QVBoxLayout, QWidget, QDialog, QFileDialog,
    QMessageBox, QCheckBox, QLabel, QDialogButtonBox, QLineEdit, QColorDialog, QComboBox, QDoubleSpinBox
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
- Remove first and waste fractions
- Tabs
- Add run log as annotations
- Different colors for each shading area/labels?
- Sheeps
- Shade volume option for when fractions aren't present
- Change fonts?
- Custom y labels
- More complete error messages
- Sort fraction label appearance
- Only show fraction labels if they are within the x range currently shown
- Add custom legend labels
- Settings in dialogs should be remembered if closed and reopened again

'''

class AnalyseDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Analyse")

        # Create layout
        self.layout = QVBoxLayout()

        title = QLabel("Analyse")
        font = QFont()
        font.setBold(True)
        font.setPointSize(16)
        title.setFont(font)
        self.layout.addWidget(title)
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
    xLimitChanged = pyqtSignal(float, float)
    yLimitChanged = pyqtSignal(float, float)
    resetXLimits = pyqtSignal()
    resetYLimits = pyqtSignal()

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
        self.add_legend_checkbox.setChecked(False)  # Legend off by default

        self.add_fraction_labels_checkbox.stateChanged.connect(self.toggle_fraction_labels)
        self.add_legend_checkbox.stateChanged.connect(self.toggle_legend)

        self.layout.addWidget(self.add_fraction_labels_checkbox)
        self.layout.addWidget(self.add_legend_checkbox)

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

        # Section: Shade Fractions
        shade_fractions_label = QLabel("Shade Fractions")
        shade_fractions_label.setFont(self._create_bold_font(12))
        self.layout.addWidget(shade_fractions_label)

        self.start_fraction_label = QLabel("Start Fraction")
        self.start_fraction_input = QLineEdit()
        self.stop_fraction_label = QLabel("Stop Fraction")
        self.stop_fraction_input = QLineEdit()

        self.layout.addWidget(self.start_fraction_label)
        self.layout.addWidget(self.start_fraction_input)
        self.layout.addWidget(self.stop_fraction_label)
        self.layout.addWidget(self.stop_fraction_input)

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

    def _create_bold_font(self, size):
        bold_font = QFont()
        bold_font.setBold(True)
        bold_font.setPointSize(size)
        return bold_font

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


class SelectCurvesDialog(QDialog):
    curveOptionsChanged = pyqtSignal(dict)

    def __init__(self, curves, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Curves")

        self.curves = curves
        self.parent = parent

        self.main_layout = QVBoxLayout()
        self.checkboxes = {}
        self.curve_options = {}
        excluded_curves = {'Injection', 'Run Log', 'Fraction', 'UV_CUT_TEMP@100,BASEM'}

        # Controls for UV curve
        self.setup_uv_controls()

        for curve in self.curves:
            if curve not in excluded_curves and curve != 'UV':
                self.setup_curve_controls(curve)

        self.setLayout(self.main_layout)

    def setup_uv_controls(self):
        # Add linestyle options for UV
        linestyle_combo = QComboBox()
        linestyle_combo.addItems(['-', '--', '-.', ':'])
        linestyle_combo.setCurrentIndex(0)
        linestyle_combo.setFixedWidth(50)
        linestyle_combo.currentIndexChanged.connect(lambda index, c='UV': self.handle_linestyle_change(c)(index))

        # Add linewidth options for UV
        linewidth_box = QDoubleSpinBox()
        linewidth_box.setRange(0.5, 5.0)
        linewidth_box.setSingleStep(0.5)
        linewidth_box.setValue(1.5)
        linewidth_box.setFixedWidth(50)
        linewidth_box.valueChanged.connect(lambda value, c='UV': self.handle_linewidth_change(c)(value))

        # Add custom y-label input for UV
        ylabel_edit = QLineEdit()
        ylabel_edit.setPlaceholderText("Custom Y label")
        ylabel_edit.editingFinished.connect(lambda c='UV': self.handle_ylabel_change(c, ylabel_edit.text()))

        # Add color picker for UV
        color_button = QPushButton("Color")
        color_button.clicked.connect(lambda _, c='UV': self.handle_color_change(c)())

        # Layout for UV controls
        uv_layout = QHBoxLayout()
        uv_layout.addWidget(QLabel('UV:'))
        uv_layout.addWidget(linestyle_combo)
        uv_layout.addWidget(linewidth_box)
        uv_layout.addWidget(ylabel_edit)
        uv_layout.addWidget(color_button)
        self.main_layout.addLayout(uv_layout)

        # Initialize UV curve options
        self.curve_options['UV'] = {
            'linestyle': '-',
            'linewidth': 1.5,
            'ylabel': 'UV (mAU)',
            'color': 'black'}

    def setup_curve_controls(self, curve):
        checkbox = QCheckBox(curve)
        checkbox.setChecked(False)
        checkbox.stateChanged.connect(self.update_curve_selection)

        # Add linestyle options
        linestyle_combo = QComboBox()
        linestyle_combo.addItems(['-', '--', '-.', ':'])
        linestyle_combo.setCurrentIndex(0)
        linestyle_combo.setFixedWidth(50)
        linestyle_combo.currentIndexChanged.connect(lambda index, c=curve: self.handle_linestyle_change(c)(index))

        # Add linewidth options
        linewidth_box = QDoubleSpinBox()
        linewidth_box.setRange(0.5, 5.0)
        linewidth_box.setSingleStep(0.5)
        linewidth_box.setValue(1.5)
        linewidth_box.setFixedWidth(50)
        linewidth_box.valueChanged.connect(lambda value, c=curve: self.handle_linewidth_change(c)(value))

        # Add custom y-label input for curve
        ylabel_edit = QLineEdit()
        ylabel_edit.setPlaceholderText("Custom Y label")
        ylabel_edit.editingFinished.connect(lambda c=curve: self.handle_ylabel_change(c, ylabel_edit.text()))


        # Add color picker button
        color_button = QPushButton(f"Color")
        color_button.clicked.connect(lambda _, c=curve: self.handle_color_change(c)())

        # Layout for the curve options
        hbox = QHBoxLayout()
        hbox.addWidget(checkbox)
        hbox.addWidget(linestyle_combo)
        hbox.addWidget(linewidth_box)
        hbox.addWidget(ylabel_edit)
        hbox.addWidget(color_button)

        self.main_layout.addLayout(hbox)
        self.checkboxes[curve] = checkbox
        self.curve_options[curve] = {
            'linestyle': '-',
            'linewidth': 1.5,
            'ylabel': curve,
            'color': 'black'}

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

    def update_curve_selection(self, state):
        selected_curves = {}

        for curve, checkbox in self.checkboxes.items():
            if checkbox.isChecked():
                selected_curves[curve] = self.curve_options[curve]

        # Always include UV curve options
        selected_curves['UV'] = self.curve_options['UV']

        self.curveOptionsChanged.emit(selected_curves)


class SingleMode(QDialog):
    def __init__(self, mode_name, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Single Mode")
        
        self.mode_name = mode_name
        self.loaded_file = None
        self.data = None
        self.show_legend = False
        self.show_fraction_labels = False
        self.options_state = {
            'Add fraction labels': False,
            'Add Legend': False
        }

        self.colors = ['r', 'g', 'b', 'c', 'm']

        self.shaded_regions = []
        self.show_shaded_fractions = False
        self.selected_curves = {'UV': {'linestyle': '-', 'linewidth': 1.5, 'color': 'black', 'ylabel': 'UV (mAU)'}}
        
        self.select_curves_dialog = None
        self.options_dialog = None

        self.xmin = None
        self.xmax = None
        self.ymin = None
        self.ymax = None

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
        self.select_curves_button = QPushButton("Select Curves")
        self.analyse_button = QPushButton("Analyse")
        self.back_button = QPushButton("Back")

        # Add buttons to the button layout
        self.button_layout.addWidget(self.load_data_button)
        self.button_layout.addWidget(self.clear_data_button)
        self.button_layout.addWidget(self.save_plot_button)
        self.button_layout.addWidget(self.options_button)
        self.button_layout.addWidget(self.select_curves_button)
        self.button_layout.addWidget(self.analyse_button)
        self.button_layout.addWidget(self.back_button)

        # Create a matplotlib figure and canvas
        self.figure = plt.figure(figsize=(7,3.5))
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
        self.select_curves_button.clicked.connect(self.open_select_curves_dialog)
        self.analyse_button.clicked.connect(self.open_analyse_dialog)
        self.back_button.clicked.connect(self.close_dialog)

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
        self.selected_curves = {'UV': self.selected_curves.get('UV', {'linestyle': '-', 'linewidth': 1.5, 'color': 'black', 'ylabel': 'UV (mAU)'})}

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
        if 'UV' in self.data:
            uv_options = self.selected_curves.get('UV', {'linestyle': '-', 'linewidth': 1.5, 'color': 'black', 'ylabel': 'UV (mAU)'})
            curvekeys = list(self.data['UV'].keys())
            x = np.array(self.data['UV'][curvekeys[0]])
            y = np.array(self.data['UV'][curvekeys[1]])
            
            uv_line, = ax.plot(x, y, label='UV', color=uv_options['color'], linestyle=uv_options['linestyle'], linewidth=uv_options['linewidth'])
            ax.set_xlim(left=0, right=max(x))
            ax.set_ylabel(uv_options['ylabel'], color=uv_options['color'])
            ax.tick_params(axis='y', labelcolor=uv_options['color'])
            handles.append(uv_line)
            labels.append('UV')

        # Apply custom limits if set, else use default limits
        if self.xmin is not None or self.xmax is not None:
            ax.set_xlim(left=self.xmin, right=self.xmax)
        else:
            ax.set_xlim(left=0, right=max(x))

        if self.ymin is not None or self.ymax is not None:
            ax.set_ylim(bottom=self.ymin, top=self.ymax)

        # Plot selected curves with customization options
        y_axes = [ax]

        for i, (curve, options) in enumerate(self.selected_curves.items()):
            if curve != 'UV' and curve in self.data:
                linestyle = options.get('linestyle', '-')
                linewidth = options.get('linewidth', 1.5)
                color = options.get('color', self.colors[i % len(self.colors)])
                ylabel = options.get('ylabel', curve)

                curvekeys = list(self.data[curve].keys())
                x = np.array(self.data[curve][curvekeys[0]])
                y = np.array(self.data[curve][curvekeys[1]])

                if len(y_axes) == 1:
                    new_ax = ax.twinx()
                    y_axes.append(new_ax)
                elif len(y_axes) > 1:
                    new_ax = ax.twinx()
                    new_ax.spines['right'].set_position(('outward', 40 * len(y_axes)))
                    y_axes.append(new_ax)

                try:
                    line, = new_ax.plot(x, y, label=curve, color=color, linestyle=linestyle, linewidth=linewidth)
                except Exception as e:
                    print("Error plotting curve:", e)
                new_ax.set_ylabel(ylabel, color=color)
                new_ax.tick_params(axis='y', labelcolor=color)

                handles.append(line)
                labels.append(curve)

        ax.set_xlabel('Volume (mL)')

        if self.show_legend:
            ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.12), ncol=10, fontsize=8, handles=handles, labels=labels)

        if self.show_fraction_labels:
            self.add_fractions()

        if self.show_shaded_fractions:
            self.add_shaded_regions()

        plt.tight_layout()
        self.canvas.draw()

    def clear_data(self):
        if self.options_dialog:
            self.options_dialog.close()

        if self.loaded_file:
            self.loaded_file = None
            self.data = None
            self.selected_curves = {}
            self.figure.clear()
            if self.select_curves_dialog is not None:
                self.select_curves_dialog.close()
                self.select_curves_dialog = None
            print("All data cleared.")
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

    def save_plot(self):
        if not self.is_data_loaded():
            return        
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

    def set_shaded_fractions_visibility(self, start_frac, stop_frac):
        if not self.is_data_loaded():
            return        
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

        # Get the corresponding volume ranges
        start_index = fractions.index(start_frac)
        stop_index = fractions.index(stop_frac)
        start_vol = volumes[start_index]
        stop_vol = volumes[stop_index]

        # Store the actual volumes for shading
        self.shaded_regions.append((start_vol, stop_vol))  # Store volumes instead of indices
        self.show_shaded_fractions = True

        # Update the plot
        self.update_plot()

    def add_shaded_regions(self):
        if not self.is_data_loaded():
            return        
        if not self.shaded_regions:
            return
        
        for start_vol, stop_vol in self.shaded_regions:
            # Shade the area under the curve between the start and stop volumes
            xdata, ydata = self.ax1.lines[0].get_data()  # Assuming the UV curve is the first plotted line
            mask = (xdata >= start_vol) & (xdata <= stop_vol)
            self.ax1.fill_between(xdata[mask], ydata[mask], color='grey', alpha=0.5)

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
        analyse_dialog = AnalyseDialog(self)

        analyse_dialog.move(self.x() + 250, self.y() + 450)
        analyse_dialog.show()


class OverlayMode(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Overlay Mode")

        # Create layout
        self.layout = QVBoxLayout()

        self.layout.addWidget(QLabel("Overlay Mode"))
        self.layout.addWidget(QLabel("Functionality yet to be added"))

        # Add buttons
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.layout.addWidget(self.button_box)

        # Set the layout
        self.setLayout(self.layout)


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
