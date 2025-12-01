
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QSizePolicy
)

from PySide6.QtCore import QSettings, Qt


class PreviewZone(QWidget):
    """
    A custom QWidget designed to accept dragged files and display them 
    in a scrollable grid area, simulating a file system view.
    """
    # Callback function to notify the parent window of image file changes
    update_main_window_list = None 

    def __init__(self):
        super().__init__()
        
        # --- Crucial step for Drag-and-Drop ---
        # self.setAcceptDrops(True)
        
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

    #     # Scroll area for displaying images
    #     self.scroll_area = QScrollArea()
    #     self.scroll_area.setWidgetResizable(True)
    #     self.scroll_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
    #     self.scroll_area.setStyleSheet("border: 1px solid #ddd; background-color: #f0f0f0;")
        
    #     # Inner widget that holds the image QGridLayout layout
    #     self.image_container_widget = QWidget()
    #     self.image_layout = QGridLayout(self.image_container_widget)
    #     self.image_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft) 
    #     self.scroll_area.setWidget(self.image_container_widget)
        
    #     self.main_layout.addWidget(self.scroll_area)

    # # --- 1. DnD Step: Check if the dragged item is a file ---
    # def dragEnterEvent(self, event: QDragEnterEvent):
    #     """Accepts the drag if it contains acceptable file paths (URIs)."""
    #     if event.mimeData().hasUrls():
    #         can_accept = any(
    #             url.isLocalFile() and url.toLocalFile().lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))
    #             for url in event.mimeData().urls()
    #         )
            
    #         if can_accept:
    #             event.acceptProposedAction()
    #             self.instruction_label.setStyleSheet("border: 2px dashed #4CAF50; padding: 20px; color: #4CAF50;")
    #         else:
    #             event.ignore()
    #     else:
    #         event.ignore()

    # # Reset border style when dragging leaves
    # def dragLeaveEvent(self, event):
    #     self.instruction_label.setStyleSheet("border: 2px dashed #aaa; padding: 20px; color: #555;")
    #     event.accept()

    # # --- 2. DnD Step: Process the dropped files ---
    # def dropEvent(self, event: QDropEvent):
    #     """Handles the actual drop operation by storing paths and triggering redrawing."""
        
    #     # Clear existing images and stored paths
    #     self.image_files.clear()

    #     for url in event.mimeData().urls():
    #         if url.isLocalFile():
    #             file_path = url.toLocalFile()
    #             self.image_files.append(file_path)

    #     # CRITICAL FIX: Use the callback to notify the MainWindow
    #     if self.update_main_window_list:
    #          self.update_main_window_list(self.image_files)

    #     # Redraw the grid with the new set of images
    #     self.recalculate_and_redraw()

    #     # Reset instruction label style
    #     self.instruction_label.setStyleSheet("border: 2px dashed #aaa; padding: 20px; color: #555;")
    #     event.acceptProposedAction()
        
    # # --- Handle Scroll Wheel for Zooming (MODIFIED) ---
    # def wheelEvent(self, event: QWheelEvent):
    #     """Resizes the thumbnails based on the scroll wheel movement, only if Ctrl is pressed."""
        
    #     # Check if the Ctrl key is pressed
    #     if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            
    #         delta = event.angleDelta().y()
    #         new_size = self.thumbnail_size
            
    #         if delta > 0: # Scroll up (Zoom In)
    #             new_size += self.size_step
    #         elif delta < 0: # Scroll down (Zoom Out)
    #             new_size -= self.size_step
            
    #         # Clamp the size within the min/max bounds
    #         new_size = max(self.min_size, min(self.max_size, new_size))
            
    #         if new_size != self.thumbnail_size:
    #             self.thumbnail_size = new_size
    #             # Recalculate item width based on the new thumbnail size
    #             self.ITEM_WIDTH = int(self.thumbnail_size * 1.1) # Adjusted multiplier
                
    #             # Rebuild the grid with the new size and updated column count
    #             self.recalculate_and_redraw()
                
    #             event.accept()
    #         else:
    #             event.accept() 
    #     else:
    #         # If Ctrl is NOT pressed, pass the event up to the scroll area 
    #         super().wheelEvent(event)

    # # --- Handle resizing for dynamic columns ---
    # def resizeEvent(self, event):
    #     """Called automatically when the widget size changes."""
    #     self.recalculate_and_redraw()
    #     super().resizeEvent(event)
        
    # def recalculate_and_redraw(self):
    #     """
    #     Calculates the new maximum number of columns and rebuilds the grid.
    #     """
    #     if not self.image_files:
    #         return

    #     available_width = self.scroll_area.viewport().width() - 20
        
    #     if available_width >= self.ITEM_WIDTH:
    #         new_columns = max(1, available_width // self.ITEM_WIDTH)
    #     else:
    #         new_columns = 1
        
    #     # Only redraw if the number of columns or size has changed
    #     if new_columns != self.current_columns or self.image_layout.count() == 0:
    #         self.current_columns = new_columns
    #         self.clear_images()

    #         # Iterate through collected files and display them in the grid
    #         for i, file_path in enumerate(self.image_files):
    #             row = i // self.current_columns
    #             col = i % self.current_columns
    #             self.display_image(file_path, row, col)

    # def clear_images(self):
    #     """Removes all image widgets from the scroll area."""
    #     while self.image_layout.count():
    #         item = self.image_layout.takeAt(0)
    #         if item.widget():
    #             item.widget().deleteLater()
        
    # def display_image(self, file_path, row, col):
    #     """Loads, resizes, and displays an image from the given path in a specific grid cell."""
        
    #     try:
    #         pil_image = Image.open(file_path)
    #         pil_image.thumbnail((self.thumbnail_size, self.thumbnail_size))
    #         q_image = ImageQt.toqpixmap(pil_image)
            
    #         image_label = QLabel()
    #         image_label.setPixmap(q_image)
    #         image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
    #         # FILENAME LABEL REMOVED (Requirement 3)
            
    #         # Container fixed size uses thumbnail size for a tighter grid
    #         image_container = QWidget()
    #         image_container.setFixedSize(self.ITEM_WIDTH, self.ITEM_WIDTH) 
            
    #         container_layout = QVBoxLayout(image_container)
    #         container_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignCenter)
    #         container_layout.addWidget(image_label)
    #         # Filename label widget removed here
            
    #         self.image_layout.addWidget(image_container, row, col)
            
    #     except Exception as e:
    #         print(f"Error loading image {file_path}: {e}")

