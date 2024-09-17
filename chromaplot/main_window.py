'''
ChromaPlot Version 0.1.1
Authors: Billy Hobbs and Felipe Ossa
© 2024 Billy Hobbs. All rights reserved.
'''

from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QWidget, QDialog
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt
import sys
import os

from chromaplot.single_mode import SingleMode
from chromaplot.overlay_mode import OverlayMode

class MainWindow(QMainWindow):
    def __init__(self, version):
        super().__init__()
        self.setWindowTitle("ChromaPlot")

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
        welcome_label = QLabel(f"Welcome to ChromaPlot (Version {version})")
        welcome_label.setAlignment(Qt.AlignCenter)
        welcome_label.setFont(QFont("Arial", 16, QFont.Bold))
        main_layout.addWidget(welcome_label)

        main_layout.addSpacing(10)

        overall_description = QLabel(
            "A tool for easily creating high-quality chromatogram figures with data exported from Cytiva Akta systems."
        ) 

        overall_description.setAlignment(Qt.AlignCenter)
        overall_description.setWordWrap(True)
        main_layout.addWidget(overall_description)

        main_layout.addSpacing(10)

        # Add information about the modes
        info_label = QLabel("<b><span style='font-size:14pt'>Select a mode to get started:</span></b>")
        info_label.setFont(QFont("Arial", 14))
        main_layout.addWidget(info_label)

        # Create buttons for the modes
        self.single_mode_button = QPushButton("Single Mode")
        self.overlay_mode_button = QPushButton("Overlay Mode")

        # Create a layout for the buttons
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.single_mode_button)
        button_layout.addWidget(self.overlay_mode_button)

        # Add the button layout to the main layout
        main_layout.addLayout(button_layout)

        main_layout.addSpacing(10) 

        # Add descriptions for the modes
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

        # Add a link to GitHub and email
        github_link = QLabel()
        github_link.setText('Please report issues on <a href="https://github.com/beh22/ChromaPlot/">GitHub</a> or <a href="mailto:billyehobbs@gmail.com">email us</a>')
        github_link.setOpenExternalLinks(True)
        github_link.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(github_link)

        about_button_layout = QHBoxLayout()
        about_button_layout.setAlignment(Qt.AlignCenter)
        about_button = QPushButton("About")
        about_button_layout.addWidget(about_button)
        about_button.clicked.connect(self.open_about_dialog)
        main_layout.addLayout(about_button_layout)

        # Add a copyright label at the bottom
        # copyright_label = QLabel("© 2024 Billy Hobbs. All rights reserved.")
        # copyright_label.setAlignment(Qt.AlignCenter)
        # copyright_label.setStyleSheet("font-size: 10px; color: grey;")

        # Add copyright label to the main layout
        # main_layout.addWidget(copyright_label)        

        # Set the layout to a central widget
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # Connect the buttons to their respective methods
        self.single_mode_button.clicked.connect(self.single_mode)
        self.overlay_mode_button.clicked.connect(self.overlay_mode)

    def resource_path(self, relative_path):
        if hasattr(sys, '_MEIPASS'):
            return os.path.join(sys._MEIPASS, relative_path)
        return os.path.join(os.path.abspath("./chromaplot/resources/"), relative_path)

    def single_mode(self):
        self.single_mode_dialog = SingleMode("Single Mode", self)
        self.hide()
        self.single_mode_dialog.show()

    def overlay_mode(self):
        self.overlay_mode_dialog = OverlayMode(self)
        self.hide()
        self.overlay_mode_dialog.exec_()

    def open_about_dialog(self):
        about_dialog = AboutDialog(self)
        about_dialog.exec_()
        # about_dialog.show()

class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About ChromaPlot")

        layout = QVBoxLayout()

        about_text = QLabel(
            "ChromaPlot Version 0.1.0\n\n"
            "Authors: Billy Hobbs and Felipe Ossa\n"
            "© 2024 Billy Hobbs.  All rights reserved.\n\n"
            "ChromaPlot is a tool for creating high-quality chromatogram figures.\n\n"
            "For more information,  please visit our GitHub repository."
        )
        about_text.setAlignment(Qt.AlignLeft)
        about_text.setWordWrap(True)
        layout.addWidget(about_text)

        self.setLayout(layout)