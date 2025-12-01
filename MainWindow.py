

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QSizePolicy
)

from PySide6.QtCore import QSettings, Qt
from PySide6.QtGui import QIntValidator

from PreviewZone import *


class MainWindow(QMainWindow):
    def __init__(self,):
        super().__init__()
        
        # --- QSettings setup ---
        self.app_name = "ImageSlideshow"
        self.settings = QSettings("orgName", "appName")
        
        self.setWindowTitle("Image Slideshow")

        # Slideshow Settings
        self.count = 10
        self.time = 10
        

        self.load_settings()



        validator = QIntValidator(1, 100)


        
        # # Instantiate the separate slideshow window


        # self.slideshow_window = SlideshowWindow(
        #     # Pass the stop method as a callback
        #     close_callback=self._handle_slideshow_close
        # )
        # self.slideshow_window.show()

        # Main widget and layout
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        
      

        # --- Section 1: Slideshow Controls ---

        control_group = QWidget()
        control_layout = QHBoxLayout(control_group)
        control_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        # Time Textbox
        control_layout.addWidget(QLabel("Time per image (s):"))
        self.time_input = QLineEdit(str(self.time)) 
        self.time_input.setValidator(validator) 
        self.time_input.setMaximumWidth(80)
        control_layout.addWidget(self.time_input)

        # Count Textbox
        control_layout.addWidget(QLabel("Number of images:"))
        self.count_input = QLineEdit(str(self.count))
        self.count_input.setValidator(validator)
        self.count_input.setMaximumWidth(80)
        control_layout.addWidget(self.count_input)

        # Start Button
        self.start_button = QPushButton("Start Session")
        self.start_button.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        # self.start_button.clicked.connect(self.start_slideshow)
        control_layout.addWidget(self.start_button)

        control_layout.addStretch(1)
        

        main_layout.addWidget(control_group)
        # main_layout.addWidget(self.create_separator())
        main_layout.addSpacerItem()

        # --- Section 2: Image Preview Zone ---
        
        self.image_drop_widget = PreviewZone() ## TEMP
        # self.image_drop_widget = ImageDropWidget()
        # Pass the method reference for file list update
        # self.image_drop_widget.update_main_window_list = self._update_image_files
        
        self.image_drop_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        main_layout.addWidget(self.image_drop_widget)

        

        self.setCentralWidget(main_widget)



    def load_settings(self):
        """Loads window geometry count and time from QSettings."""
        
        if self.settings is not None:
            self.restoreGeometry(self.settings.value("geometry"))
            self.count = self.settings.value("count")
            self.time = self.settings.value("time")

        else:
            # Default settings
            self.setGeometry(100, 100, 700, 500) 
            self.count = 10
            self.time = 10


            

    def closeEvent(self, event):
        """Saves window geometry to QSettings and closes the secondary window."""
        # if self.timer.isActive():
        #     self.timer.stop()
        
        # Close the secondary window gracefully
        # self.slideshow_window.close()
        
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("count", self.count_input.text())
        self.settings.setValue("time", self.time_input.text())

        event.accept()


    def create_separator(self):
        """Utility to create a horizontal rule for visual separation."""
        separator = QWidget()
        separator.setFixedHeight(1)
        separator.setStyleSheet("background-color: #ccc;")
        return separator