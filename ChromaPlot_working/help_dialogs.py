'''
ChromaPlot Version 0.1.0
Authors: Billy Hobbs and Felipe Ossa
© 2024 Billy Hobbs. All rights reserved.
'''

from PyQt5.QtWidgets import (
     QDialog, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QDialog, QLabel, QTabWidget
)
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt

import sys
import os

class MainHelpDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("ChromaPlot Help")

        self.single_mode_help_dialog = None
        self.overlay_mode_help_dialog = None

        # Create the main layout
        main_layout = QVBoxLayout()

        # Add the logo
        logo_label = QLabel()
        logo_path = self.resource_path("cp_logo.png")
        logo_pixmap = QPixmap(logo_path)
        desired_width = 300
        desired_height = 150
        scaled_logo_pixmap = logo_pixmap.scaled(desired_width, desired_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        logo_label.setPixmap(scaled_logo_pixmap)
        logo_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(logo_label)

        # Add a welcome message
        welcome_label = QLabel(f"Welcome to ChromaPlot Help!")
        welcome_label.setAlignment(Qt.AlignCenter)
        welcome_label.setFont(QFont("Arial", 16, QFont.Bold))
        main_layout.addWidget(welcome_label)

        main_layout.addSpacing(10)

        overall_description = QLabel(
            "<p>ChromaPlot is a tool designed for plotting and analysing chromatographic data exported from "
            "Cytiva’s UNICORN software, used to run AKTA’s.</p>"
        )

        overall_description.setAlignment(Qt.AlignCenter)
        overall_description.setWordWrap(True)
        main_layout.addWidget(overall_description)

        main_layout.addSpacing(10)

        info_label = QLabel("<b><span style='font-size:14pt'>Select a mode to get started:</span></b>")
        info_label.setFont(QFont("Arial", 14))
        main_layout.addWidget(info_label)

        single_mode_description = QLabel(
            "<b><span style='font-size:14pt'>Single Mode:</span></b> Create plots of single datasets. Add and remove traces, with customisable options."
        )
        overlay_mode_description = QLabel(
            "<b><span style='font-size:14pt'>Overlay Mode:</span></b> Overlay and customise multiple datasets for easy comparison."
        )
        single_mode_description.setWordWrap(True)
        overlay_mode_description.setWordWrap(True)
        main_layout.addWidget(single_mode_description)
        main_layout.addWidget(overlay_mode_description)

        main_layout.addSpacing(10)

        # Create buttons for the modes
        self.single_mode_button = QPushButton("Single Mode Help")
        self.overlay_mode_button = QPushButton("Overlay Mode Help")

        # Create a layout for the buttons
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.single_mode_button)
        button_layout.addWidget(self.overlay_mode_button)

        # Add the button layout to the main layout
        main_layout.addLayout(button_layout)

        main_layout.addSpacing(10)         

        # Add a link to GitHub and email
        github_link = QLabel()
        github_link.setText('Please report issues on <a href="https://github.com/beh22/ChromaPlot/">GitHub</a> or <a href="mailto:billyehobbs@gmail.com">email us</a>')
        github_link.setOpenExternalLinks(True)
        github_link.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(github_link)

        # Add a copyright label at the bottom
        copyright_label = QLabel("© 2024 Billy Hobbs. All rights reserved.")
        copyright_label.setAlignment(Qt.AlignCenter)
        copyright_label.setStyleSheet("font-size: 10px; color: grey;")

        # Add copyright label to the main layout
        main_layout.addWidget(copyright_label)

        self.setLayout(main_layout)

        # Connect the buttons to their respective methods
        self.single_mode_button.clicked.connect(self.open_single_mode_help)
        self.overlay_mode_button.clicked.connect(self.open_overlay_mode_help)

    def open_single_mode_help(self):
        if self.single_mode_help_dialog:
            self.single_mode_help_dialog.close()

        self.single_mode_help_dialog = SingleModeHelpDialog(self)
        self.single_mode_help_dialog.show()

    def open_overlay_mode_help(self):
        if self.overlay_mode_help_dialog:
            self.overlay_mode_help_dialog.close()

        self.overlay_mode_help_dialog = OverlayModeHelpDialog(self)
        self.overlay_mode_help_dialog.show()

    def resource_path(self, relative_path):
        """ Helper function to find the logo resource path. """
        if hasattr(sys, '_MEIPASS'):
            return os.path.join(sys._MEIPASS, relative_path)
        return os.path.join(os.path.abspath("./resources/"), relative_path)

class SingleModeHelpDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Single Mode Help")
        self.setGeometry(100, 100, 600, 400)

        self.tab_widget = QTabWidget()

        self.tab_widget.addTab(self.create_general_tab(), "General")
        self.tab_widget.addTab(self.create_plotting_tab(), "Plotting")
        self.tab_widget.addTab(self.create_options_tab(), "Display Options")
        self.tab_widget.addTab(self.create_analysis_tab(), "Analysis")

        layout = QVBoxLayout()
        layout.addWidget(self.tab_widget)
        self.setLayout(layout)

    def create_general_tab(self):
        general_tab = QWidget()
        layout = QVBoxLayout()

        general_label = QLabel()
        general_label.setWordWrap(True)
        general_label.setText(
            "<h2>Single Mode</h2>"
            "<p>This is Single Mode, where you can load a single dataset, customise your plot, "
            "analyse it with various tools (more to come), and export it to create high-quality figures.</p>"
            "<p>Here’s a quick overview of the features:</p>"
            "<ul>"
            "<li><b>Load Data:</b> Import your dataset to start plotting.</li>"
            "<li><b>Clear Data:</b> Remove the current dataset and reset the plot.</li>"
            "<li><b>Save Plot:</b> Save the current plot as an image file.</li>"
            "<li><b>Display Options:</b> Customise plot settings, such as axis limits, figure legend, and shaded areas.</li>"
            "<li><b>Select Curves:</b> Choose which curves to display and customise their appearance.</li>"
            "<li><b>Analyse:</b> Tools for deeper analysis of your data.</li>"
            "</ul>"
        )

        layout.addWidget(general_label)
        layout.addStretch()
        general_tab.setLayout(layout)
        return general_tab

    def create_plotting_tab(self):
        plotting_tab = QWidget()
        layout = QVBoxLayout()

        plotting_label = QLabel()
        plotting_label.setWordWrap(True)
        plotting_label.setText(
            "<h2>Plotting in Single Mode</h2>"
            "<p><b>Load Data:</b> Click 'Load Data' and navigate to select the dataset you would like to plot. "
            "The file to load should be one exported from UNICORN and have .txt, .asc, or .csv file extensions. "
            "Exports from multiple versions of UNICORN are supported.</p>"
            "<p>Once loaded, the UV curve from the dataset will be automatically plotted. "
            "You can add other curves by selecting the checkboxes in the 'Select Curves' window.</p>"
            "<p><b>Customise Curves:</b> In the 'Select Curves' window, you can choose the line style, line width, and "
            "colour of each curve. You can also choose the y-axis label and the label used in the figure legend for each curve.</p>"
            "<p>Further customisation of the plot can be achieved using the 'Display Options' window.</p>"
            "<p><b>Save Plot:</b> When you are happy with the appearance of your plot, press 'Save Plot'. "
            "Plots can be saved as .pdf, .png, or .jpg files.</p>"
        )

        layout.addWidget(plotting_label)
        layout.addStretch()
        plotting_tab.setLayout(layout)
        return plotting_tab

    def create_options_tab(self):
        options_tab = QWidget()
        layout = QVBoxLayout()

        options_label = QLabel()
        options_label.setWordWrap(True)
        options_label.setText(
            "<h2>Display Options</h2>"
            "<p>The 'Display Options' window allows you to fine-tune the appearance of your plot:</p>"
            "<ul>"
            "<li><b>Add Legend:</b> Toggle the display of the legend on the plot. You can place the legend above the plot "
            "or in the 'best-fit' location as determined by Matplotlib.</li>"
            "<li><b>Add Fraction Labels:</b> If fractions were collected for this dataset, you can display their locations on the plot. "
            "This is useful for determining which areas to shade if desired.</li>"
            "<li><b>Define Limits:</b> Manually set the minimum and maximum values for the x and y axes. "
            "You can apply these settings or reset them to the default range defined by the size of the dataset.</li>"
            "<li><b>Shading:</b> Highlight specific regions of the UV plot by shading them. "
            "You can shade by fractions or specific volumes, and customise the colour and transparency of the shading. "
            "You can undo the last shaded area or clear all shading."
            "<i>Note:</i> Shading by fractions for datasets where fractions were collected in 96-well plates is not currently supported. "
            "However, you can still display fraction labels and shade by volume based on this.</li>"
        )

        layout.addWidget(options_label)
        layout.addStretch()
        options_tab.setLayout(layout)
        return options_tab

    def create_analysis_tab(self):
        analysis_tab = QWidget()
        layout = QVBoxLayout()

        analysis_label = QLabel()
        analysis_label.setWordWrap(True)
        analysis_label.setText(
            "<h2>Analysis</h2>"
            "<p>The 'Analyse' button provides tools to investigate your data more closely:</p>"
            "<ul>"
            "<li><b>Vertical Marker:</b> Place a vertical line on the plot to mark a specific volume. "
            "You can move this marker across the x-axis to see the corresponding y-values for each curve. "
            "As you move the vertical marker, the y-values for all displayed curves at that specific volume are shown.</li>"
            "</ul>"
            "<p>More tools will be added to 'Analyse' in the future.</p>"
        )

        layout.addWidget(analysis_label)
        layout.addStretch()
        analysis_tab.setLayout(layout)
        return analysis_tab

class OverlayModeHelpDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Overlay Mode Help")
        self.setGeometry(100, 100, 600, 400)

        self.tab_widget = QTabWidget()

        self.tab_widget.addTab(self.create_general_tab(), "General")
        self.tab_widget.addTab(self.create_plotting_tab(), "Plotting")
        self.tab_widget.addTab(self.create_options_tab(), "Display Options")
        self.tab_widget.addTab(self.create_analysis_tab(), "Analysis")

        layout = QVBoxLayout()
        layout.addWidget(self.tab_widget)
        self.setLayout(layout)

    def create_general_tab(self):
        general_tab = QWidget()
        layout = QVBoxLayout()

        general_label = QLabel()
        general_label.setWordWrap(True)
        general_label.setText(
            "<h2>Overlay Mode</h2>"
            "<p>This is Overlay Mode, where you can load multiple datasets to easily compare them. "
            "They can then be customised, and the plot exported to create high-quality figures.</p>"
            "<p>Here’s a quick overview of the features:</p>"
            "<ul>"
            "<li><b>Load Data:</b> Import multiple datasets to load onto the plot.</li>"
            "<li><b>Clear Data:</b> Remove the current dataset and reset the plot.</li>"
            "<li><b>Save Plot:</b> Save the current plot as an image file.</li>"
            "<li><b>Display Options:</b> Customise plot settings, such as axis limits, figure legend, and shaded areas.</li>"
            "<li><b>Select Curves:</b> Choose which datasets to display and customise their appearance.</li>"
            "</ul>"
        )

        layout.addWidget(general_label)
        layout.addStretch()
        general_tab.setLayout(layout)
        return general_tab

    def create_plotting_tab(self):
        plotting_tab = QWidget()
        layout = QVBoxLayout()

        plotting_label = QLabel()
        plotting_label.setWordWrap(True)
        plotting_label.setText(
            "<h2>Plotting in Overlay Mode</h2>"
            "<p><b>Load Data:</b> Multiple datasets can be loadeded at once. "
            "Click 'Load Data' and navigate to select datasets you would like to plot. "
            "The files to load should be one exported from UNICORN and have .txt, .asc, or .csv file extensions. "
            "Exports from multiple versions of UNICORN are supported.</p>"
            "<p>Once loaded, the UV curve from the dataset will be automatically plotted. "
            "To overlay a new dataset, select this dataset through 'Load Data' and it will automatically be added.</p>"
            "<p><b>Customise Curves:</b> In the 'Select Curves' window, you can toggle which curves are currently "
            "being shown on the plot using the checkboxes. You can also choose the line style, line width, and colour of each curve. "
            "You can also choose the label used in the figure legend for each dataset.</p>"
            "<p>Further customisation of the plot can be achieved using the 'Display Options' window.</p>"
            "<p><b>Save Plot:</b> When you are happy with the appearance of your plot, press 'Save Plot'. "
            "Plots can be saved as .pdf, .png, or .jpg files.</p>"
        )

        layout.addWidget(plotting_label)
        layout.addStretch()
        plotting_tab.setLayout(layout)
        return plotting_tab

    def create_options_tab(self):
        options_tab = QWidget()
        layout = QVBoxLayout()

        options_label = QLabel()
        options_label.setWordWrap(True)
        options_label.setText(
            "<h2>Display Options</h2>"
            "<p>The 'Display Options' window allows you to fine-tune the appearance of your plot:</p>"
            "<ul>"
            "<li><b>Add Legend:</b> Toggle the display of the legend on the plot. You can place the legend above the plot "
            "or in the 'best-fit' location as determined by Matplotlib.</li>"
            "<li><b>Y-Axis Label:</b> Change the label for the y-axis.</li>"
            "<li><b>Define Limits:</b> Manually set the minimum and maximum values for the x and y axes. "
            "You can apply these settings or reset them to the default range defined by the size of the dataset.</li>"
            "<li><b>Shading:</b> Highlight specific regions of the UV plot by shading them. "
            "You can shade by fractions or specific volumes, and customise the colour and transparency of the shading. "
            "You can undo the last shaded area or clear all shading."
            "<i>Note:</i> Shading by fractions for datasets where fractions were collected in 96-well plates is not currently supported. "
            "However, you can still display fraction labels and shade by volume based on this.</li>"
        )

        layout.addWidget(options_label)
        layout.addStretch()
        options_tab.setLayout(layout)
        return options_tab
    
    def create_analysis_tab(self):
        analysis_tab = QWidget()
        layout = QVBoxLayout()

        analysis_label = QLabel()
        analysis_label.setWordWrap(True)
        analysis_label.setText(
            "<h2>Analysis</h2>"
            "<p>The 'Analyse' button provides tools to investigate your data more closely:</p>"
            "<ul>"
            "<li><b>Vertical Marker:</b> Place a vertical line on the plot to mark a specific volume. "
            "You can move this marker across the x-axis to see the corresponding y-values for each curve. "
            "As you move the vertical marker, the y-values for all displayed curves at that specific volume are shown. <br>"
            "<b>NOTE: the vertical marker in Overlay Mode is a work in progress. It contains multiple known bugs</b></li>"
            "</ul>"
            "<p>More tools will be added to 'Analyse' in the future.</p>"
        )

        layout.addWidget(analysis_label)
        layout.addStretch()
        analysis_tab.setLayout(layout)
        return analysis_tab
