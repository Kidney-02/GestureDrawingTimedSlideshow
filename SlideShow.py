from PySide6.QtWidgets import( 
    QWidget, QVBoxLayout, QLabel, QSizePolicy,
    QPushButton, QHBoxLayout
    )
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, QTimer
from PIL import Image, ImageQt


class SlideShowWidget(QWidget):
    """
    An Overlay that displays the images in a sequence using the predetermined parameters.
    """
    def __init__(self, parent=None): 
        super().__init__(parent)

        # Parameters
        self.image_files = []
        self.image_loaded = None
        self.time = 0


        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setStyleSheet("background-color: rgba(180, 162, 40, 0.55); border: none; margin: 0px; padding: 0px;")
        layout = QVBoxLayout(self)
        
        # Image Display
        self.display_label = QLabel()

        
        layout.addWidget(self.display_label)
        
        
        # Clear Button
        self.clear_button = QPushButton("Stop Images")
        self.clear_button.setStyleSheet("""
            QWidget {
                color: white; font-weight: bold;
            }
            QPushButton {
                background-color: #555; 
            }
            QPushButton:hover {
                background-color: #666;
            }    
            QPushButton:pressed {
                background-color: #444;
            }                                        
        """
        )
        self.clear_button.setMaximumWidth(100)
        # self.clear_button.clicked.connect(self._relay_signal)

        control_group = QWidget()
        control_layout = QHBoxLayout(control_group)
        control_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        control_layout.addWidget(self.clear_button)

        layout.addWidget(control_group)




    def update_geometry(self):
        """Called by the parent to ensure the overlay covers the entire area."""
        if self.parentWidget():
            pass
        self.setGeometry(self.parentWidget().rect())


    def show(self):
        
        self.update_geometry()
        super().show()
    

    def resizeEvent(self, event):
        """Ensure the overlay is resized and positioned whenever the parent resizes."""
        
        self.update_geometry()        
        super().resizeEvent(event)


    def display_image(self, file_path, current_image_num, total_images, time_per_image_s):
        """
        Loads and displays the image in the SlideshowWindow, resizing it 
        to fit the current window size.
        """
        try:
            # Get the size of the central display area
            label_size = self.display_label.size()
            
            # Load image using PIL
            pil_image = self.image_loaded.copy()
            
            # Use Pillow's thumbnail to resize while maintaining aspect ratio
            pil_image.thumbnail((label_size.width(), label_size.height())) 
            
            # Convert to QPixmap
            q_image = ImageQt.toqpixmap(pil_image)
            
            # Update the display label
            self.display_label.setPixmap(q_image)


        except Exception as e:
            print(f"Error loading slideshow image {file_path}: {e}")
            # Fallback text if the image fails to load
            self.display_label.setPixmap(QPixmap()) 
            self.display_label.setText(f"Error: Could not load image file.") 
            self.display_label.setStyleSheet("color: red; font-size: 16pt;")


    def start_slide_show(self, image_files:list, time:int):
        
        self.image_files = image_files
        self.image_loaded = self.load_image_file(self.image_files[0])
        self.time = time

        pass


    def load_image_file(self, file_path:str):
        
        self.image_loaded = Image.open(file_path)

        pass


    # def _update_status_label(self, current_image_num, total_images):
    #     self.status_label.setText(
    #         f"Image {current_image_num} of {total_images}\n"
    #         f"Time Left: {self.current_countdown_time}s"
    #     )
    #     self.status_label.raise_() # Ensures it's always visible over the image


    # def _update_countdown(self):
    #     self.current_countdown_time -= 1
    #     # ... (handling for current_countdown_time < 0 and stopping timer)

    #     # Update only the time part of the label
    #     current_text = self.status_label.text()
    #     lines = current_text.split('\n')
    #     if len(lines) > 0:
    #         image_info = lines[0] # "Image X of Y"
    #         self.status_label.setText(
    #             f"{image_info}\n"
    #             f"Time Left: {self.current_countdown_time}s"
    #         )
    #     self.status_label.raise_()
