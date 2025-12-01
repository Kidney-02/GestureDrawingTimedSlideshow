
import os

from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QGridLayout, QLabel
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, QTimer
from PIL import Image, ImageQt


class SlideshowWindow(QMainWindow):
    """A separate, dark-mode window to display the random slideshow images."""
    def __init__(self, close_callback=None): 
        super().__init__()
        self.close_callback = close_callback # Store the callback
        self.setWindowTitle("Slideshow Display (Dark Mode)")
        self.setGeometry(850, 100, 600, 600)  # Positioned next to main window

        # --- Dark Mode Styling ---
        self.setStyleSheet("""
            QMainWindow { background-color: #1e1e1e; }
            QLabel { color: #f0f0f0; padding: 10px; }
        """)

        # Main Display Label
        self.display_label = QLabel("Waiting for Slideshow to Start...", 
                                    alignment=Qt.AlignmentFlag.AlignCenter)
        self.display_label.setMinimumSize(400, 400)
        self.display_label.setStyleSheet("font-size: 16pt; font-weight: bold; border: none;") # Removed border
        
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        layout.addWidget(self.display_label)
        self.setCentralWidget(central_widget)

        # Status label for image count and countdown
        self.status_label = QLabel("", alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)
        self.status_label.setStyleSheet("color: #FFD700; font-size: 12pt; background-color: rgba(0,0,0,100); padding: 5px;")
        self.status_label.setContentsMargins(10, 10, 10, 10)

        overlay_layout = QGridLayout(central_widget)
        # ...
        overlay_layout.addWidget(self.display_label, 0, 0)
        # Place status label in the same cell (0, 0) but aligned top-right
        overlay_layout.addWidget(self.status_label, 0, 0, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)
        
        self.countdown_timer = QTimer(self)
        self.countdown_timer.timeout.connect(self._update_countdown)
        self.current_countdown_time = 0
        self.total_image_display_time_s = 0


        
    def display_image(self, file_path, current_image_num, total_images, time_per_image_s):
        """
        Loads and displays the image in the SlideshowWindow, resizing it 
        to fit the current window size.
        """
        try:
            # Get the size of the central display area
            label_size = self.display_label.size()
            
            # Load image using PIL
            pil_image = Image.open(file_path)
            
            # Use Pillow's thumbnail to resize while maintaining aspect ratio
            # Use the available label size for scaling
            pil_image.thumbnail((label_size.width(), label_size.height())) 
            
            # Convert to QPixmap
            q_image = ImageQt.toqpixmap(pil_image)
            
            # Update the display label
            self.display_label.setPixmap(q_image)
            
            # FILENAME TEXT REMOVED (Requirement 2 & Fix 1)
            # The pixmap is now the sole content.

            self.total_image_display_time_ms = time_per_image_s
            self.current_countdown_time = time_per_image_s // 1000 

            self._update_status_label(current_image_num, total_images)
            self.countdown_timer.start(1000) # Start 1-second interval timer


        except Exception as e:
            print(f"Error loading slideshow image {file_path}: {e}")
            # Fallback text if the image fails to load
            self.display_label.setPixmap(QPixmap()) 
            self.display_label.setText(f"Error: Could not load image file.") 
            self.display_label.setStyleSheet("color: red; font-size: 16pt;")
    def _update_status_label(self, current_image_num, total_images):
        self.status_label.setText(
            f"Image {current_image_num} of {total_images}\n"
            f"Time Left: {self.current_countdown_time}s"
        )
        self.status_label.raise_() # Ensures it's always visible over the image

    def _update_countdown(self):
        self.current_countdown_time -= 1
        # ... (handling for current_countdown_time < 0 and stopping timer)

        # Update only the time part of the label
        current_text = self.status_label.text()
        lines = current_text.split('\n')
        if len(lines) > 0:
            image_info = lines[0] # "Image X of Y"
            self.status_label.setText(
                f"{image_info}\n"
                f"Time Left: {self.current_countdown_time}s"
            )
        self.status_label.raise_()


    def closeEvent(self, event):
        """Handles closing the slideshow window if the main window closes."""
        if self.close_callback:
            # Call the function in the MainWindow to stop the timer
            self.close_callback()
        event.accept()