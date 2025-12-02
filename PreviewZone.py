
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QSizePolicy,
    QScrollArea, QGridLayout, QFrame
)
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QWheelEvent, QPalette
from PySide6.QtCore import Qt
from PIL import Image, ImageQt



class OverlayWidget(QWidget):
    """The widget that will serve as the translucent overlay."""
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 1. Set the background to be translucent green with dashed Border
        self.setStyleSheet("background-color: rgba(76, 175, 80, 0.55); border: 2px dashed rgb(76, 175, 80);")
        
        # 2. Add a message label to the center
        self.label = QLabel(
            "Drop Image Files Here (PNG, JPG, GIF)", 
            alignment=Qt.AlignmentFlag.AlignCenter
        )
        self.label.setStyleSheet("color: white; font-size: 24px;")
        
        layout = QVBoxLayout(self)
        layout.addWidget(self.label)
        
        # Start hidden
        self.hide() 

    def update_parent_geometry(self):
        """Called by the parent to ensure the overlay covers the entire area."""
        if self.parentWidget():
            self.setGeometry(self.parentWidget().rect())


class ScrollArea(QScrollArea):
    """
    Custom ScrollArea Widget that won't scroll when CTRL is held. Works with parent that will ignore regular scrolling.
    Would be ideal if could intercept the ScrollEvent from reaching Scroll area and call the scrollArea wheel event from parent
    """
    def __init__(self):
        super().__init__()

        pass
    
    # --- Handle Scroll Wheel for Zooming ---
    def wheelEvent(self, event: QWheelEvent):
        """Resizes the thumbnails based on the scroll wheel movement, only if Ctrl is pressed."""

        # Check if the Ctrl key is pressed
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            
            event.ignore()

        else:
            # If Ctrl is NOT pressed, pass the event up to the scroll area 
            super().wheelEvent(event)
            pass


class PreviewZone(QWidget):
    """
    A custom Widget designed to accept dragged files and display them 
    in a scrollable grid area, simulating a file system view.
    """
    # Callback function to notify the parent window of image file changes
    update_main_window_list = None 

    def __init__(self):
        super().__init__()

        # --- Crucial step for Drag-and-Drop ---
        self.setAcceptDrops(True)
        


        # Store file paths to allow redrawing on resize
        self.image_files = []
        
        # Image Size Control Attributes
        self.min_size = 50
        self.max_size = 400
        self.size_step = 20
        self.thumbnail_size = 200 # Initial size       
        

        # Store the currently used number of columns
        self.current_columns = 0
        
        # The minimum width required for one image container (thumbnail_size * 1.2)
        self.item_width = self.get_item_width() 




        # Main layout for the drop zone
        self.main_layout = QVBoxLayout(self)
      

        # Scroll area for displaying images
        self.scroll_area = ScrollArea()
        self.scroll_area.installEventFilter(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        # self.scroll_area.setStyleSheet("border: 1px solid #aaa; padding: default;")
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


        # Drop Zone Around Scroll Area
        self.drop_zone = QWidget()
        self.drop_zone.setObjectName("dropZone") # Need name to set style without breaking scrollarea and others
        self.drop_zone.setStyleSheet("""
            #dropZone{
                border: 2px dashed #aaa;
                padding: 5px;
                border-radius: 4px;
            }
        """)
        
        self.drop_zone_layout = QVBoxLayout(self.drop_zone)
        self.drop_zone_layout.addWidget(self.scroll_area)


        self.main_layout.addWidget(self.drop_zone)

        # --- The Overlay ---
        self.overlay = OverlayWidget(self)
        self.overlay.update_parent_geometry()
        self.overlay.hide() # Set overlay hidden on Start




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
                # Show the overlay
                self.overlay.show()
                # Ensure it stays on top
                self.overlay.raise_()
            else:
                event.ignore()
        else:
            event.ignore()

    # Reset border style when dragging leaves
    def dragLeaveEvent(self, event):
        # Hide the overlay
        self.overlay.hide()
        super().leaveEvent(event)

        event.accept()

    # --- 2. DnD Step: Process the dropped files ---
    def dropEvent(self, event: QDropEvent):
        """Handles the actual drop operation by storing paths and triggering redrawing."""
        
        # Clear existing images and stored paths
        # Later jut add to the list
        # self.image_files.clear()

        for url in event.mimeData().urls():
            if url.isLocalFile():
                file_path = url.toLocalFile()
                if file_path not in self.image_files:
                    self.image_files.append(file_path)

        

        if self.update_main_window_list:
             self.update_main_window_list(self.image_files)

        
        # Reset instruction label style
        self.overlay.hide()

        # Redraw the grid with the new set of images
        self.recalculate_and_redraw(True)

        event.acceptProposedAction()

        
    def recalculate_and_redraw(self, force_redraw:bool = False):
        """
        Calculates the new maximum number of columns and rebuilds the grid.
        """
        if not self.image_files:
            return
        
        
        available_width = self.get_available_width()
        self.item_width = self.get_item_width()

        print(available_width, self.item_width)
        
        if available_width >= self.item_width:
            new_columns = max(1, available_width // self.item_width)
        else:
            new_columns = 1

        print(new_columns)
        
        # Only redraw if the number of columns or size has changed
        if new_columns != self.current_columns or self.image_layout.count() == 0 or force_redraw:
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
            
            
            # Container fixed size uses thumbnail size for a tighter grid
            image_container = QWidget()
            image_container.setStyleSheet("border: none; padding: 0px")
            image_container.setFixedSize(self.item_width, self.item_width) 
            
            container_layout = QVBoxLayout(image_container)
            container_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignCenter)
            container_layout.addWidget(image_label)
            
            self.image_layout.addWidget(image_container, row, col)
            
        except Exception as e:
            print(f"Error loading image {file_path}: {e}")

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

                # print(self.thumbnail_size)
                
                # Rebuild the grid with the new size and updated column count

                
                event.accept()
            else:
                event.accept() 
        else:
            # If Ctrl is NOT pressed, pass the event up to the scroll area 
            event.ignore() 
            pass
    


    # --- Resize Event ---
    def resizeEvent(self, event):
        """Ensure the overlay is resized and positioned whenever the parent resizes."""
        self.recalculate_and_redraw()
        self.overlay.update_parent_geometry()
        
        super().resizeEvent(event)
        

    def load_settings(self, settings):
        """Loads window geometry count and time from QSettings."""
        

        if settings is not None:

            self.image_files = settings.value("images")
            self.thumbnail_size = settings.value("image_size")
            # self.current_columns = settings.value("columns")

            self.recalculate_and_redraw(True)

        else:
            return
            print("very sad")


    def save_settings(self):

        settings = {}
        if not self.image_files:
            settings.update({"images": []})
        else :
            settings.update({"images": self.image_files})

        if not self.thumbnail_size:
            settings.update({"image_size": 200})
        else :
            settings.update({"image_size": self.thumbnail_size})

        
        

        return settings
        




