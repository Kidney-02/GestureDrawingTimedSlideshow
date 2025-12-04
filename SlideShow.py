from PySide6.QtWidgets import( 
    QWidget, QLabel, QSizePolicy,
    QPushButton, QVBoxLayout, QHBoxLayout, QGridLayout,
    QStyle
    )
from PySide6.QtGui import QPixmap, QPainter, QColor, Qt, QIcon
from PySide6.QtCore import(
    Qt, QTimer, QSize, QPropertyAnimation,
    QEasingCurve, QPoint
    )
from PIL import Image, ImageQt


class SlideShowWidget(QWidget):
    """
    An Overlay that displays the images in a sequence using the predetermined parameters.
    """
    def __init__(self, parent=None): 
        super().__init__(parent)

        self.parent = parent

        # Parameters
        self.image_files = []
        self.loaded_image = QPixmap
        self.time = 0

        self.is_playing = True
        self.is_control_visible = True


        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        # self.setStyleSheet("background-color: rgba(180, 162, 40, 0.55); border: none; margin: 0px; padding: 0px;")


        layout = QGridLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)


        # --- 1. Display Layer ---
        # Display image here
        self.display_label = QLabel()
        self.display_label.setAlignment(Qt.AlignmentFlag.AlignCenter)        
        self.display_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.display_label.setWordWrap(True)
        self.display_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                color: #546E7A
            }
        """)

        layout.addWidget(self.display_label, 0, 0)


        # --- 2. Top Layer (The Button Container) ---

        self.button_overlay_container = QWidget()
        self.button_overlay_container.setSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed
        )
        self.button_overlay_container.setStyleSheet("""
            QWidget {
                background-color: rgba(0, 0, 0, 50);
                border-radius: 4px;
                padding: 10px;
            }
        """)

        # Create the animation object, targeting the widget's position (b"pos")
        self.animation = QPropertyAnimation(self.button_overlay_container, b"pos")
        self.animation.setDuration(300) # 300 milliseconds for a quick slide
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic) # Smoother slide


        # Button Layout within the Overlay Container
        button_layout = QHBoxLayout(self.button_overlay_container)
        button_layout.setContentsMargins(10, 10, 10, 10)
        button_layout.setSpacing(2)


        self.btn_back = self.create_icon_button(icon = QStyle.SP_MediaSkipBackward)
        self.btn_play = self.create_icon_button(icon = QStyle.SP_MediaPause)
        self.btn_play.clicked.connect(self.play_pause)
        self.btn_skip = self.create_icon_button(icon = QStyle.SP_MediaSkipForward)
        self.btn_stop = self.create_icon_button(icon = QStyle.SP_MediaStop)
        self.btn_stop.clicked.connect(parent.reset_stack)
        self.btn_hide = self.create_icon_button(icon = QStyle.SP_ArrowDown)
        self.btn_hide.clicked.connect(self.hide_overlay_box)


        button_layout.addWidget(self.btn_back)
        button_layout.addWidget(self.btn_play)
        button_layout.addWidget(self.btn_skip)
        button_layout.addWidget(self.btn_stop)
        button_layout.addWidget(self.btn_hide)


        layout.addWidget(
            self.button_overlay_container, 
            0, 0, 
            Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter
        )




    def mousePressEvent(self, event):

        if not self.is_control_visible:
            self.show_overlay_box()
        else:
            self.hide_overlay_box()
        
        # self.is_control_visible = not self.is_control_visible

        return super().mousePressEvent(event)
    

    def change_visibility(self):
        self.is_control_visible = not self.is_control_visible

        
    def hide_overlay_box(self):
        """Slides out (down) the semi-transparent button container."""

        # Stop any active animation
        self.animation.stop()

        # Disconnect any previous connections (e.g., from a show animation)
        try:
            self.animation.finished.disconnect()
        except TypeError:
            pass

        
        # Set start and end points for the slide down
        x_pos = self.button_overlay_container.x()
        y_start = self.button_overlay_container.y()
        y_end = y_start + self.button_overlay_container.height()
        self.animation.setStartValue(QPoint(x_pos, y_start))
        self.animation.setEndValue(QPoint(x_pos, y_end))
        

        # Connect a lambda function to hide the widget only after the animation is done
        self.animation.finished.connect(lambda: (
            self.button_overlay_container.move(x_pos, y_end), # Final snap to position
            self.button_overlay_container.hide(),
            self.animation.finished.disconnect(), # Clean up connection
            self.change_visibility()
        ))
        
        self.animation.start()
        

    def show_overlay_box(self):
        """Slides in (up) the semi-transparent button container."""
        
        self.animation.stop()

        # Disconnect any lingering hide connections
        try:
            self.animation.finished.disconnect()
        except TypeError:
            pass 

        # Set start and end points for the slide up
        x_pos = self.button_overlay_container.x()
        y_start = self.button_overlay_container.y()
        y_end = y_start - self.button_overlay_container.height()
        self.animation.setStartValue(QPoint(x_pos, y_start))
        self.animation.setEndValue(QPoint(x_pos, y_end))

        self.animation.finished.connect(lambda: (
            self.button_overlay_container.move(x_pos, y_end),
            self.animation.finished.disconnect(),
            self.change_visibility()
        ))

        
        self.button_overlay_container.show()
        self.animation.start()


    def play_pause(self):
        """Play and Pause the timer and change button Icon"""
        style = self.btn_play.style()

        if self.is_playing:
            # Pause if Playing
            # Display Play icon if paused because you unpause when clicking
            icon = style.standardIcon(QStyle.SP_MediaPlay)
        else:
            # Play if Paused
            icon = style.standardIcon(QStyle.SP_MediaPause)

        self.is_playing = not self.is_playing
        self.btn_play.setIcon(icon)

        return


    def create_icon_button(self, icon:QStyle.StandardPixmap = None, tooltip:str = "", parent = None, size:tuple = (50,50)) -> QPushButton:
        """
        Creates a standard QPushButton with a system stock icon.
        
        :param icon: QStyle.StandardPixmap identifier (e.g., QStyle.SP_MediaSkipForward)
        :param tooltip: The text to show on hover.
        :return: A configured QPushButton instance.
        """
        button = QPushButton(parent)

        button.setStyleSheet("""           
            QPushButton {
                background-color: rgba(0, 0, 0, 30); 
            }
            QPushButton:hover {
                background-color: rgba(80, 80, 80, 30);
            }    
            QPushButton:pressed {
                background-color: rgba(0, 0, 0, 40);
            }                                        
        """
        )

        # 1. Get the stock icon from the application's current style
        style = button.style()
        icon = style.standardIcon(icon)
        
        # 2. Set the icon and icon size
        button.setIcon(icon)
        button.setIconSize(QSize(size[0] * 0.7, size[1] * 0.7))
        
        # Set appearance and size
        button.setFixedSize(QSize(size[0], size[1]))
        button.setToolTip(tooltip)
        button.setCursor(Qt.PointingHandCursor)
        
        
        return button


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
            pil_image = self.loaded_image.copy()
            
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
        """ Start slideshow from parent window """
        
        self.image_files = image_files
        self.time = time


        self.load_image_file(self.image_files[0])
        self.update_display_image()

        # Wait 2 seconds and start timer


        pass


    def load_image_file(self, file_path:str) -> Image:        

        try:
            image = Image.open(file_path)
            image = ImageQt.toqpixmap(image)
        # image = ImageQt.toqpixmap(image)
        except Exception as e:
            print(f"Error loading image {file_path}: {e}")
            pass

        self.loaded_image = image

        return image


    def resizeEvent(self, event):

        self.update_display_image()


        return super().resizeEvent(event)
    
    
    def update_display_image(self):

        if not self.loaded_image:
            return

        # get window size and calculate image resolution
        size = self.size()

        image_scaled = self.loaded_image.scaled(
            size, 
            Qt.KeepAspectRatio, 
            Qt.SmoothTransformation
        )
        self.display_label.setPixmap(image_scaled)

        
        return image_scaled




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



