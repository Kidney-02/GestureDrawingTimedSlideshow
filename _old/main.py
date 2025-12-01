import sys
# import os
import random 
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QLineEdit, QPushButton, QScrollArea, QSizePolicy, QGridLayout,
    QMessageBox 
)
from PySide6.QtGui import QPixmap, QDragEnterEvent, QDropEvent, QWheelEvent
from PySide6.QtCore import Qt, QUrl, QSettings, QTimer, QSize
from PIL import Image, ImageQt


# import from separate py files
from mainWindow import MainWindow
from slideShowWindow import SlideshowWindow



if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # QSettings initialization
    app.setOrganizationName("MyAppOrg")
    app.setApplicationName("ImageDropper")
    
    # Define an integer validator globally for the QLineEdit widgets
    from PySide6.QtGui import QIntValidator
    QApplication.instance().IntValidator = QIntValidator(1, 999999)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())