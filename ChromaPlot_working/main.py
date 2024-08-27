'''
ChromaPlot Version 1.0.0
Authors: Billy Hobbs and Felipe Ossa
© 2024 Billy Hobbs. All rights reserved.
'''

import sys
from PyQt5.QtWidgets import QApplication
from main_window import MainWindow
from update_checker import check_for_updates, prompt_for_update
import os

'''
To do:
- Remove first and waste fractions
- Tabs
- Add run log as annotations
- Sheeps
- Change fonts?
- More complete error messages
- Add different tabs to options dialog
- Sort stylesheet!

- Add option to pick which column is automatically plotted?

- Finish vertical marker
- Search for updates
- Improve help page
- Shading to overlay mode
- Add toggle legend position to overlay mode

- Don't crash if there are no fractions - sort of fixed

- Shade fractions with silly numbering from 96 well fraction things

- Warning when changing modes
'''


global_stylesheet = """
QWidget {
    background-color: #3e3e3e;
}

QFrame#plotFrame {
    border: 3px solid #7e7e7e;
    padding: 0px;
    margin: 0px;
    border-radius: 5px;
}

QTextEdit {
    background-color: white;
}

QLabel {
    color: white;
}

QPushButton {
    background-color: #7e7e7e;
    color: white;
    font-weight: bold;
    border-radius: 5px;
    padding: 5px;
}

QPushButton:hover {
    background-color: #d39333;
}

QLineEdit {
    background-color: white;
    color: black;
    border: 2px solid #AA4A44;
    padding: 5px;
    border-radius: 5px;
}

QComboBox {
    border: 2px #AA4A44;
    border-radius: 3px;
    padding: 5px;
    background-color: white;  
    color: black;  
}

QComboBox:hover {
    border: 2px solid #d39333;  
}

QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 20px;
    border-left: 1px solid gray;
    background-color: white;  
}

QComboBox::down-arrow {
    width: 10px;
    height: 10px;
    color: black;  
}

QComboBox QAbstractItemView {
    background-color: white;  
    selection-background-color: #d39333;  
    selection-color: white;  
    border: 1px solid gray;
}

QCheckBox {
    color: white;
}

QDoubleSpinBox, QSpinBox {
    background-color: white;
    color: black;
    border: 2px solid #AA4A44;
    padding: 5px;
    border-radius: 5px;
}

QRadioButton {
    color: white;
}

"""


version = '1.0.0'

def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(global_stylesheet)
    window = MainWindow(version)
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()