
import random 
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QLineEdit, QPushButton, QScrollArea, QSizePolicy, QGridLayout,
    QMessageBox 
)
from PySide6.QtGui import QPixmap, QDragEnterEvent, QDropEvent, QWheelEvent
from PySide6.QtCore import Qt, QSettings, QTimer, QSize
from PIL import Image, ImageQt

from SlideShow import SlideshowWindow


class ImageDropWidget(QWidget):
    """
    A custom QWidget designed to accept dragged files and display them 
    in a scrollable grid area, simulating a file system view.
    """
    # Callback function to notify the parent window of image file changes
    update_main_window_list = None 

    def __init__(self):
        super().__init__()
        
        # --- Crucial step for Drag-and-Drop ---
        self.setAcceptDrops(True)
        
        # Image Size Control Attributes
        self.min_size = 50
        self.max_size = 400
        self.size_step = 20
        self.thumbnail_size = 200 # Initial size
        
        # Store file paths to allow redrawing on resize
        self.image_files = []
        # Store the currently used number of columns
        self.current_columns = 0
        
        # The minimum width required for one image container (thumbnail_size * 1.2)
        # Note: Reduced multiplier since file name label is removed
        self.ITEM_WIDTH = int(self.thumbnail_size * 1.1) 

        # Main layout for the drop zone
        self.main_layout = QVBoxLayout(self)

        # Drop instruction label
        self.instruction_label = QLabel(
            "Drop Image Files Here (PNG, JPG, GIF)", 
            alignment=Qt.AlignmentFlag.AlignCenter
        )
        self.instruction_label.setStyleSheet("border: 2px dashed #aaa; padding: 20px; color: #555;")
        self.main_layout.addWidget(self.instruction_label)

        # Scroll area for displaying images
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.scroll_area.setStyleSheet("border: 1px solid #ddd; background-color: #f0f0f0;")
        
        # Inner widget that holds the image QGridLayout layout
        self.image_container_widget = QWidget()
        self.image_layout = QGridLayout(self.image_container_widget)
        self.image_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft) 
        self.scroll_area.setWidget(self.image_container_widget)
        
        self.main_layout.addWidget(self.scroll_area)

    # --- 1. DnD Step: Check if the dragged item is a file ---
    def dragEnterEvent(self, event: QDragEnterEvent):
        """Accepts the drag if it contains acceptable file paths (URIs)."""
        if event.mimeData().hasUrls():
            can_accept = any(
                url.isLocalFile() and url.toLocalFile().lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))
                for url in event.mimeData().urls()
            )
            
            if can_accept:
                event.acceptProposedAction()
                self.instruction_label.setStyleSheet("border: 2px dashed #4CAF50; padding: 20px; color: #4CAF50;")
            else:
                event.ignore()
        else:
            event.ignore()

    # Reset border style when dragging leaves
    def dragLeaveEvent(self, event):
        self.instruction_label.setStyleSheet("border: 2px dashed #aaa; padding: 20px; color: #555;")
        event.accept()

    # --- 2. DnD Step: Process the dropped files ---
    def dropEvent(self, event: QDropEvent):
        """Handles the actual drop operation by storing paths and triggering redrawing."""
        
        # Clear existing images and stored paths
        self.image_files.clear()

        for url in event.mimeData().urls():
            if url.isLocalFile():
                file_path = url.toLocalFile()
                self.image_files.append(file_path)

        # CRITICAL FIX: Use the callback to notify the MainWindow
        if self.update_main_window_list:
             self.update_main_window_list(self.image_files)

        # Redraw the grid with the new set of images
        self.recalculate_and_redraw()

        # Reset instruction label style
        self.instruction_label.setStyleSheet("border: 2px dashed #aaa; padding: 20px; color: #555;")
        event.acceptProposedAction()
        
    # --- Handle Scroll Wheel for Zooming (MODIFIED) ---
    def wheelEvent(self, event: QWheelEvent):
        """Resizes the thumbnails based on the scroll wheel movement, only if Ctrl is pressed."""
        
        # Check if the Ctrl key is pressed
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            
            delta = event.angleDelta().y()
            new_size = self.thumbnail_size
            
            if delta > 0: # Scroll up (Zoom In)
                new_size += self.size_step
            elif delta < 0: # Scroll down (Zoom Out)
                new_size -= self.size_step
            
            # Clamp the size within the min/max bounds
            new_size = max(self.min_size, min(self.max_size, new_size))
            
            if new_size != self.thumbnail_size:
                self.thumbnail_size = new_size
                # Recalculate item width based on the new thumbnail size
                self.ITEM_WIDTH = int(self.thumbnail_size * 1.1) # Adjusted multiplier
                
                # Rebuild the grid with the new size and updated column count
                self.recalculate_and_redraw()
                
                event.accept()
            else:
                event.accept() 
        else:
            # If Ctrl is NOT pressed, pass the event up to the scroll area 
            super().wheelEvent(event)

    # --- Handle resizing for dynamic columns ---
    def resizeEvent(self, event):
        """Called automatically when the widget size changes."""
        self.recalculate_and_redraw()
        super().resizeEvent(event)
        
    def recalculate_and_redraw(self):
        """
        Calculates the new maximum number of columns and rebuilds the grid.
        """
        if not self.image_files:
            return

        available_width = self.scroll_area.viewport().width() - 20
        
        if available_width >= self.ITEM_WIDTH:
            new_columns = max(1, available_width // self.ITEM_WIDTH)
        else:
            new_columns = 1
        
        # Only redraw if the number of columns or size has changed
        if new_columns != self.current_columns or self.image_layout.count() == 0:
            self.current_columns = new_columns
            self.clear_images()

            # Iterate through collected files and display them in the grid
            for i, file_path in enumerate(self.image_files):
                row = i // self.current_columns
                col = i % self.current_columns
                self.display_image(file_path, row, col)

    def clear_images(self):
        """Removes all image widgets from the scroll area."""
        while self.image_layout.count():
            item = self.image_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
    def display_image(self, file_path, row, col):
        """Loads, resizes, and displays an image from the given path in a specific grid cell."""
        
        try:
            pil_image = Image.open(file_path)
            pil_image.thumbnail((self.thumbnail_size, self.thumbnail_size))
            q_image = ImageQt.toqpixmap(pil_image)
            
            image_label = QLabel()
            image_label.setPixmap(q_image)
            image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            # FILENAME LABEL REMOVED (Requirement 3)
            
            # Container fixed size uses thumbnail size for a tighter grid
            image_container = QWidget()
            image_container.setFixedSize(self.ITEM_WIDTH, self.ITEM_WIDTH) 
            
            container_layout = QVBoxLayout(image_container)
            container_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignCenter)
            container_layout.addWidget(image_label)
            # Filename label widget removed here
            
            self.image_layout.addWidget(image_container, row, col)
            
        except Exception as e:
            print(f"Error loading image {file_path}: {e}")



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # --- QSettings setup ---
        self.organization_name = "MyAppOrg"
        self.app_name = "ImageDropper"
        self.settings = QSettings(self.organization_name, self.app_name)
        
        self.setWindowTitle("PySide6 Image Dropper and Slideshow Control")
        self.load_settings()

        # Slideshow state variables
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_slideshow)
        self.image_files = [] 
        self.slides_shown_count = 0
        self.total_slides_to_show = 0
        
        # Instantiate the separate slideshow window
        self.slideshow_window = SlideshowWindow(
            # Pass the stop method as a callback
            close_callback=self._handle_slideshow_close
        )
        self.slideshow_window.show()

        # Main widget and layout
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        
        # --- Section 1: Slideshow Status Area ---
        # self.slideshow_status = QLabel("Ready. Drop images and configure the slideshow below.")
        # self.slideshow_status.setStyleSheet("font-size: 14pt; color: #007ACC; font-weight: bold;")
        # main_layout.addWidget(self.slideshow_status)
        # main_layout.addWidget(self.create_separator()) 

        # --- Section 2: Slideshow Controls (REMAINS IN MAIN WINDOW) ---
        control_group = QWidget()
        control_layout = QHBoxLayout(control_group)
        control_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        # Time Textbox
        control_layout.addWidget(QLabel("Time per image (s):"))
        self.time_input = QLineEdit("10") # DEFAULT TIME MS (10 SECONDS)
        self.time_input.setValidator(QApplication.instance().IntValidator) 
        self.time_input.setMaximumWidth(80)
        control_layout.addWidget(self.time_input)

        # Count Textbox
        control_layout.addWidget(QLabel("Number of images:"))
        self.count_input = QLineEdit("10")
        self.count_input.setValidator(QApplication.instance().IntValidator)
        self.count_input.setMaximumWidth(80)
        control_layout.addWidget(self.count_input)

        # Start Button
        self.start_button = QPushButton("Start Slideshow")
        self.start_button.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        self.start_button.clicked.connect(self.start_slideshow)
        control_layout.addWidget(self.start_button)
        control_layout.addStretch(1)

        main_layout.addWidget(control_group)
        main_layout.addWidget(self.create_separator())

        # --- Section 3: Image Drop Zone ---
        drop_zone_label = QLabel("Image Thumbnail Grid (Drop Files Here)")
        drop_zone_label.setStyleSheet("font-size: 12pt; font-weight: bold; margin-top: 10px;")
        main_layout.addWidget(drop_zone_label)
        
        self.image_drop_widget = ImageDropWidget()
        # Pass the method reference for file list update
        self.image_drop_widget.update_main_window_list = self._update_image_files
        
        self.image_drop_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        main_layout.addWidget(self.image_drop_widget)

        self.setCentralWidget(main_widget)
        
    def _update_image_files(self, files):
        """Callback to update the main window's image list after a drop event."""
        self.image_files = files

    def start_slideshow(self):
        """Initiates the timed random image slideshow."""
        if self.timer.isActive():
            self.timer.stop()
            self.start_button.setText("Start Slideshow")
            self.start_button.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
            self.slideshow_status.setText(f"Slideshow finished after {self.slides_shown_count} images.")
            
            # Hide the slideshow window when stopped
            self.slideshow_window.hide()
            return

        if not self.image_files:
            QMessageBox.warning(self, "Warning", "Please drop image files into the grid first.")
            return

        try:
            time_ms = int(self.time_input.text() )*1000
            self.current_image_display_time_ms = time_ms
            count = int(self.count_input.text())
        except ValueError:
            QMessageBox.critical(self, "Error", "Time and Image Count must be valid integers.")
            return

        if time_ms <= 0 or count <= 0:
            QMessageBox.warning(self, "Warning", "Time and Image Count must be greater than zero.")
            return
        
        self.total_slides_to_show = count
        self.slides_shown_count = 0
        
        # Show the slideshow window when starting
        self.slideshow_window.show()

        self.slideshow_window.raise_()

        self.timer.start(time_ms)
        self.start_button.setText("Stop Slideshow")
        self.start_button.setStyleSheet("background-color: #FF5733; color: white; font-weight: bold;")
        self.update_slideshow() # Show the first image immediately

    def update_slideshow(self):
        """Picks a random image and tells the SlideshowWindow to display it."""
        if self.slides_shown_count >= self.total_slides_to_show:
            self.timer.stop()
            self.start_button.setText("Start Slideshow")
            self.start_button.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
            self.slideshow_status.setText(f"Slideshow finished! ({self.slides_shown_count}/{self.total_slides_to_show} shown)")
            self.slideshow_window.hide()
            return
            
        random_path = random.choice(self.image_files)

        # Call the new method on the separate window instance
        self.slideshow_window.display_image(random_path,
                                            self.slides_shown_count, 
                                            self.total_slides_to_show,
                                            self.current_image_display_time_ms)
        
        self.slides_shown_count += 1
        self.slideshow_status.setText(f"Slideshow active: {self.slides_shown_count} of {self.total_slides_to_show} images shown.")

    def _handle_slideshow_close(self):
        """Stops the slideshow when the SlideshowWindow is closed by the user."""
        
        # The start_slideshow method is a toggle; calling it while the timer 
        # is active will stop the timer and reset the button/status.
        if self.timer.isActive():
            self.start_slideshow()

    def load_settings(self):
        """Loads window geometry from QSettings."""
        geometry = self.settings.value("geometry")
        if geometry is not None:
            self.restoreGeometry(geometry)
        else:
            # Fallback geometry if no settings are found
            self.setGeometry(100, 100, 700, 500) # Adjusted height since slideshow display moved
            
    def closeEvent(self, event):
        """Saves window geometry to QSettings and closes the secondary window."""
        if self.timer.isActive():
            self.timer.stop()
        
        # Close the secondary window gracefully
        self.slideshow_window.close()
        
        self.settings.setValue("geometry", self.saveGeometry())
        event.accept()

    def create_separator(self):
        """Utility to create a horizontal rule for visual separation."""
        separator = QWidget()
        separator.setFixedHeight(1)
        separator.setStyleSheet("background-color: #ccc;")
        return separator