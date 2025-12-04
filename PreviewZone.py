
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QSizePolicy,
    QScrollArea, QGridLayout, QFrame
)
from PySide6.QtGui import QWheelEvent, QShowEvent
from PySide6.QtCore import Qt
from PIL import ImageQt



class ScrollArea(QScrollArea):
    """
    Custom ScrollArea Widget that won't scroll when CTRL is held. Works with parent that will ignore regular scrolling.
    Would be ideal if could intercept the ScrollEvent from reaching Scroll area and call the scrollArea wheel event from parent
    """
    def __init__(self, parent):
        super().__init__(parent)

        self.parent = parent

        pass
    
    # --- Handle Scroll Wheel for Zooming ---
    def wheelEvent(self, event: QWheelEvent):
        """Resizes the thumbnails based on the scroll wheel movement, only if Ctrl is pressed."""

        # Check if the Ctrl key is pressed
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:

            delta = event.angleDelta().y()
            new_size = self.parent.thumbnail_size
            
            if delta > 0: # Scroll up (Zoom In)
                new_size += self.parent.size_step
            elif delta < 0: # Scroll down (Zoom Out)
                new_size -= self.parent.size_step
            
            available_width = self.parent.get_available_width()

            # Clamp the size within the min/max bounds
            new_size = max(self.parent.min_size, min(self.parent.max_size, new_size, available_width))
            
            if new_size != self.parent.thumbnail_size:
                self.parent.thumbnail_size = new_size
                # Recalculate item width based on the new thumbnail size
                self.parent.item_width = self.parent.get_item_width()

                # Rebuild the grid with the new size and updated column count
                self.parent.recalculate_and_redraw(True)
                
                event.accept()
            else:
                event.accept() 
        else:
            super().wheelEvent(event)
            pass


class PreviewZone(QWidget):
    """
    A custom Widget designed to accept dragged files and display them 
    in a scrollable grid area, simulating a file system view.
    """

    def __init__(self):
        super().__init__()

        self.image_thumbnails = []
        
        # Image Size Control Attributes
        self.min_size = 50
        self.max_size = 400
        self.size_step = 20
        self.thumbnail_size = 200 # Initial size

        # Store the currently used number of columns
        self.current_columns = 0
        
        # The minimum width required for one image container (thumbnail_size * 1.2)
        self.item_width = self.get_item_width() 

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Main layout for the drop zone
        self.main_layout = QVBoxLayout(self)
      

        # Scroll area for displaying images
        self.scroll_area = ScrollArea(self)
        self.scroll_area.installEventFilter(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: 1px solid #aaa; 
                padding: 2px;                
            }
        """)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        

        # Inner widget that holds the image QGridLayout layout
        self.image_container_widget = QWidget()        
        self.image_container_widget.setStyleSheet("border: none; padding: 0px;")

        self.image_layout = QGridLayout(self.image_container_widget)
        self.image_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)


        self.scroll_area.setWidget(self.image_container_widget)



        self.main_layout.addWidget(self.scroll_area)
        

        
    def recalculate_and_redraw(self, force_redraw:bool = False):
        """
        Calculates the new maximum number of columns and rebuilds the grid.
        """
        if not self.image_thumbnails:
            self.clear_images()
            return
        
        available_width = self.get_available_width()
        
        if available_width >= self.item_width:
            new_columns = max(1, available_width // self.item_width)
        else:
            new_columns = 1

        
        # Only redraw if the number of columns or size has changed
        if new_columns != self.current_columns or self.image_layout.count() == 0 or force_redraw:
            self.current_columns = new_columns
            self.clear_images()

            # Iterate through collected files and display them in the grid
            for i, img in enumerate(self.image_thumbnails):
                row = i // self.current_columns
                col = i % self.current_columns
                self.display_image(img, row, col)


    def clear_images(self):
        """Removes all image widgets from the scroll area."""
        while self.image_layout.count():
            item = self.image_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
    def display_image(self, img, row, col):
        """ resizes, and displays an image from the given path in a specific grid cell."""
        

        image_copy = img.copy()

        image_copy.thumbnail((self.thumbnail_size, self.thumbnail_size))
        q_image = ImageQt.toqpixmap(image_copy)


        image_label = QLabel()
        image_label.setPixmap(q_image)
        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        image_container = QWidget()
        image_container.setStyleSheet("border: none; padding: 0px")
        image_container.setFixedSize(self.item_width, self.item_width) 
        
        container_layout = QVBoxLayout(image_container)
        container_layout.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignCenter)
        container_layout.addWidget(image_label)

        self.image_layout.addWidget(image_container, row, col)
            

    def get_available_width(self) -> int: 
        return self.scroll_area.viewport().width() - 20
    
    def get_item_width(self) -> int:
        return int(self.thumbnail_size + 20)

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
            
            available_width = self.get_available_width()

            # Clamp the size within the min/max bounds
            new_size = max(self.min_size, min(self.max_size, new_size, available_width))
            
            if new_size != self.thumbnail_size:
                self.thumbnail_size = new_size
                # Recalculate item width based on the new thumbnail size
                self.item_width = self.get_item_width()

                # Rebuild the grid with the new size and updated column count
                self.recalculate_and_redraw(True)
                
                event.accept()
            else:
                event.ignore() 
        else:
            # If Ctrl is NOT pressed, pass the event up to the scroll area 
            event.ignore() 
            pass
    

    # --- Resize Event ---
    def resizeEvent(self, event):
        """Ensure the overlay is resized and positioned whenever the parent resizes."""
        
        self.recalculate_and_redraw()        
        super().resizeEvent(event)
    

    def showEvent(self, event: QShowEvent):
        # Call the base class implementation
        super().showEvent(event)
        
        self.recalculate_and_redraw()


    def set_image_files(self, images:dict):

        if bool(images):
            # print(f"\033[33m{images}\033[0m")
            self.image_thumbnails = images
        else:
            self.clear_image_files()
            return
        
        self.recalculate_and_redraw(True)
        pass


    def clear_image_files(self):

        self.image_thumbnails.clear()
        self.recalculate_and_redraw(True)
        pass


    
  




