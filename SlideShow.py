from PySide6.QtWidgets import( 
    QWidget, QLabel, QSizePolicy,
    QPushButton, QVBoxLayout, QHBoxLayout, QGridLayout,
    QStyle
    )
from PySide6.QtGui import QPixmap, QPainter, QColor, Qt, QIcon
from PySide6.QtCore import(
    Qt, QTimer, QSize, QPropertyAnimation,
    QEasingCurve, QPoint, QByteArray
    )
from PIL import Image, ImageQt



SVG_PLAY = """
<svg xmlns="http://www.w3.org/2000/svg" width="50" height="50" viewBox="0 0 24 24">
	<path fill="white" d="M9 15.714V8.287q0-.368.244-.588q.243-.22.568-.22q.102 0 .213.028q.11.027.211.083l5.843 3.733q.186.13.28.298q.093.167.093.379t-.093.379t-.28.298l-5.843 3.733q-.101.055-.213.083t-.213.028q-.326 0-.568-.22T9 15.714" />
</svg>
"""
SVG_PAUSE = """
<svg xmlns="http://www.w3.org/2000/svg" width="50" height="50" viewBox="0 0 24 24">
	<path fill="white" d="M15 18q-.402 0-.701-.299T14 17V7q0-.402.299-.701T15 6h1.5q.402 0 .701.299T17.5 7v10q0 .402-.299.701T16.5 18zm-7.5 0q-.402 0-.701-.299T6.5 17V7q0-.402.299-.701T7.5 6H9q.402 0 .701.299T10 7v10q0 .402-.299.701T9 18z" />
</svg>
"""
SVG_NEXT = """
<svg xmlns="http://www.w3.org/2000/svg" width="50" height="50" viewBox="0 0 24 24">
	<path fill="white" d="M4.096 15.106V8.894q0-.373.243-.59q.242-.218.565-.218q.125 0 .237.025t.217.106l4.661 3.112q.187.13.27.295t.084.376t-.083.376t-.27.295l-4.662 3.112q-.106.08-.217.106q-.112.025-.237.025q-.323 0-.565-.218q-.243-.217-.243-.59m8.885 0V8.894q0-.373.242-.59q.243-.218.566-.218q.125 0 .236.025t.217.106l4.662 3.112q.187.13.27.295t.084.376t-.084.376q-.083.164-.27.295l-4.662 3.112q-.105.08-.217.106t-.236.025q-.323 0-.566-.218q-.242-.217-.242-.59" />
</svg>
"""
SVG_BACK = """
<svg xmlns="http://www.w3.org/2000/svg" width="50" height="50" viewBox="0 0 24 24">
	<path fill="white" d="m18.642 15.783l-4.661-3.112q-.187-.13-.27-.295T13.627 12t.083-.376t.27-.295l4.662-3.112q.106-.08.218-.105q.111-.025.236-.025q.323 0 .566.217t.242.59v6.212q0 .373-.243.59q-.242.218-.565.218q-.125 0-.236-.025q-.112-.025-.218-.106m-8.884 0L5.096 12.67q-.186-.13-.27-.295T4.742 12t.084-.376q.084-.164.27-.295l4.662-3.112q.106-.08.217-.105t.237-.025q.323 0 .565.217t.242.59v6.212q0 .373-.242.59q-.242.218-.565.218q-.125 0-.237-.025t-.217-.106" />
</svg>
"""
SVG_STOP = """
<svg xmlns="http://www.w3.org/2000/svg" width="50" height="50" viewBox="0 0 24 24">
	<path fill="white" d="M7 15.385v-6.77q0-.666.475-1.14T8.615 7h6.77q.666 0 1.14.475T17 8.615v6.77q0 .666-.475 1.14t-1.14.475h-6.77q-.666 0-1.14-.475T7 15.386" />
</svg>
"""
SVG_DOWN = """
<svg xmlns="http://www.w3.org/2000/svg" width="50" height="50" viewBox="0 0 24 24">
    <path fill="white" d="m11.565 13.873l-2.677-2.677q-.055-.055-.093-.129q-.037-.073-.037-.157q0-.168.11-.289q.112-.121.294-.121h5.677q.181 0 .292.124t.111.288q0 .042-.13.284l-2.677 2.677q-.093.093-.2.143t-.235.05t-.235-.05t-.2-.143"/>
</svg>
"""


class SlideShowWidget(QWidget):
    """
    An Overlay that displays the images in a sequence using the predetermined parameters.
    """
    def __init__(self, parent=None): 
        super().__init__(parent)

        self.parent = parent

        # Parameters
        self.image_files = []
        self.loaded_image = QPixmap()
        self.time = 0

        self.is_playing = True
        self.is_control_visible = True

        self.button_appear_time = 300

        self.play_icon = self.create_icon_from_svg(SVG_PLAY)
        self.pause_icon = self.create_icon_from_svg(SVG_PAUSE)

        
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        layout = QGridLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)


        # --- 1. Display Layer ---
        # Display image here
        self.display_label = QLabel()
        self.display_label.setAlignment(Qt.AlignmentFlag.AlignCenter)        
        self.display_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.display_label.setMinimumSize(50, 50) # If not set the minimum becomes the image size
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
        self.animation.setDuration(self.button_appear_time) # 300 milliseconds for a quick slide
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic) # Smoother slide


        # Button Layout within the Overlay Container
        button_layout = QHBoxLayout(self.button_overlay_container)
        button_layout.setContentsMargins(10, 10, 10, 10)
        button_layout.setSpacing(2)


        self.btn_back = self.create_icon_button(icon = SVG_BACK)
        self.btn_play = self.create_icon_button(icon = SVG_PAUSE)
        self.btn_play.clicked.connect(self.play_pause)
        self.btn_skip = self.create_icon_button(icon = SVG_NEXT)
        self.btn_stop = self.create_icon_button(icon = SVG_STOP)
        self.btn_stop.clicked.connect(parent.reset_stack)
        self.btn_hide = self.create_icon_button(icon = SVG_DOWN)
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

        y_end = self.calculate_widget_bottom() + self.button_overlay_container.height()
        self.animation.setStartValue(QPoint(x_pos, y_start))
        self.animation.setEndValue(QPoint(x_pos, y_end))

        # print(y_end)
        

        # Connect a lambda function to hide the widget only after the animation is done
        self.animation.finished.connect(lambda: (
            self.button_overlay_container.move(x_pos, y_end), # Final snap to position
            self.button_overlay_container.hide(),
            self.animation.finished.disconnect(), # Clean up connection
        ))
        
        self.animation.start()        
        self.change_visibility()
        

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
        y_start = self.calculate_widget_bottom()
        
        y_end = y_start - self.button_overlay_container.height()
        
        # print(y_end)

        self.animation.setStartValue(QPoint(x_pos, y_start))
        self.animation.setEndValue(QPoint(x_pos, y_end))

        self.animation.finished.connect(lambda: (
            self.button_overlay_container.move(x_pos, y_end),
            self.animation.finished.disconnect(),
        ))

        
        self.button_overlay_container.show()
        self.animation.start()
        self.change_visibility()


    def calculate_widget_bottom(self) -> int:
        
        y = self.y() + self.height()
        return y


    def play_pause(self, force_play:bool = None):
        """Play and Pause the timer and change button Icon"""

        print(force_play)

        if force_play is False:
            if self.is_playing:
                # Pause if Playing
                # Display Play icon if paused because you unpause when clicking
                icon = self.play_icon
            else:
                # Play if Paused
                icon = self.pause_icon
            

            
            self.is_playing = not self.is_playing
        elif force_play:
            icon = self.pause_icon
            self.is_playing = True


        self.btn_play.setIcon(icon)

        return


    def create_icon_button(self, icon:str = None, tooltip:str = "", parent = None, size:QSize = QSize(50,50)) -> QPushButton:
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
        
        # 1. create and icon
        icon = self.create_icon_from_svg(icon)

        # 2. Set the icon and icon size
        button.setIcon(icon)
        button.setIconSize(QSize(size.width() * 0.7, size.height() * 0.7))
        
        # Set appearance and size
        button.setFixedSize(size)
        button.setToolTip(tooltip)
        button.setCursor(Qt.PointingHandCursor)
        
        
        return button

    def create_icon_from_svg(self, svg_data:str, size: QSize = QSize(80, 80)) -> QIcon:
        """
        Creates a QIcon object by loading SVG data directly from a string.
        This method uses QByteArray and QPixmap, which is the standard way
        to handle inline image data in Qt.
        """
        # Convert the Python string to a QByteArray (encoded as UTF-8)
        svg_byte_array = QByteArray(svg_data.encode('utf-8'))

        # Create a QPixmap instance
        pixmap = QPixmap(size)
        
        # Load the SVG data into the QPixmap.
        if pixmap.loadFromData(svg_byte_array, "SVG"):
            # Create and return the QIcon from the rendered QPixmap
            return QIcon(pixmap)
        else:
            # Handle case where SVG loading failed (e.g., return a fallback icon)
            print("Error: Could not load SVG data.")
            return QIcon() # Returns an empty icon


    def update_geometry(self):
        """Called by the parent to ensure the overlay covers the entire area."""
        if self.parentWidget():
            pass
        self.setGeometry(self.parentWidget().rect())


    def show(self):
        
        self.update_geometry()
        super().show()
    


    def start_slide_show(self, image_files:list, time:int):
        """ Start slideshow from parent window """
        
        self.image_files = image_files
        self.time = time


        self.load_image_file(self.image_files[0])
        self.update_display_image()
        self.play_pause(True)

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

        if self.loaded_image.isNull():
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



