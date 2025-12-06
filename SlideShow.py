from PySide6.QtWidgets import( 
    QWidget, QLabel, QSizePolicy,
    QPushButton, QVBoxLayout, QHBoxLayout, QGridLayout,
    QStyle, QFrame, QGraphicsOpacityEffect
    )
from PySide6.QtGui import QPixmap, QPainter, QColor, Qt, QIcon
from PySide6.QtCore import(
    Qt, QSize, QPropertyAnimation,
    QEasingCurve, QPoint, QByteArray,
    QTimer, QTime, QElapsedTimer
    )
from PIL import Image, ImageQt


##### --- Button100

SVG_PLAY = """
<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 24 24">
	<path fill="white" d="M9 15.714V8.287q0-.368.244-.588q.243-.22.568-.22q.102 0 .213.028q.11.027.211.083l5.843 3.733q.186.13.28.298q.093.167.093.379t-.093.379t-.28.298l-5.843 3.733q-.101.055-.213.083t-.213.028q-.326 0-.568-.22T9 15.714" />
</svg>
"""
SVG_PAUSE = """
<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 24 24">
	<path fill="white" d="M15 18q-.402 0-.701-.299T14 17V7q0-.402.299-.701T15 6h1.5q.402 0 .701.299T17.5 7v10q0 .402-.299.701T16.5 18zm-7.5 0q-.402 0-.701-.299T6.5 17V7q0-.402.299-.701T7.5 6H9q.402 0 .701.299T10 7v10q0 .402-.299.701T9 18z" />
</svg>
"""
SVG_NEXT = """
<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 24 24">
	<path fill="white" d="M4.096 15.106V8.894q0-.373.243-.59q.242-.218.565-.218q.125 0 .237.025t.217.106l4.661 3.112q.187.13.27.295t.084.376t-.083.376t-.27.295l-4.662 3.112q-.106.08-.217.106q-.112.025-.237.025q-.323 0-.565-.218q-.243-.217-.243-.59m8.885 0V8.894q0-.373.242-.59q.243-.218.566-.218q.125 0 .236.025t.217.106l4.662 3.112q.187.13.27.295t.084.376t-.084.376q-.083.164-.27.295l-4.662 3.112q-.105.08-.217.106t-.236.025q-.323 0-.566-.218q-.242-.217-.242-.59" />
</svg>
"""
SVG_BACK = """
<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 24 24">
	<path fill="white" d="m18.642 15.783l-4.661-3.112q-.187-.13-.27-.295T13.627 12t.083-.376t.27-.295l4.662-3.112q.106-.08.218-.105q.111-.025.236-.025q.323 0 .566.217t.242.59v6.212q0 .373-.243.59q-.242.218-.565.218q-.125 0-.236-.025q-.112-.025-.218-.106m-8.884 0L5.096 12.67q-.186-.13-.27-.295T4.742 12t.084-.376q.084-.164.27-.295l4.662-3.112q.106-.08.217-.105t.237-.025q.323 0 .565.217t.242.59v6.212q0 .373-.242.59q-.242.218-.565.218q-.125 0-.237-.025t-.217-.106" />
</svg>
"""
SVG_STOP = """
<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 24 24">
	<path fill="white" d="M7 15.385v-6.77q0-.666.475-1.14T8.615 7h6.77q.666 0 1.14.475T17 8.615v6.77q0 .666-.475 1.14t-1.14.475h-6.77q-.666 0-1.14-.475T7 15.386" />
</svg>
"""
SVG_DOWN = """
<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 24 24">
    <path fill="white" d="m11.565 13.873l-2.677-2.677q-.055-.055-.093-.129q-.037-.073-.037-.157q0-.168.11-.289q.112-.121.294-.121h5.677q.181 0 .292.124t.111.288q0 .042-.13.284l-2.677 2.677q-.093.093-.2.143t-.235.05t-.235-.05t-.2-.143"/>
</svg>
"""
SVG_FULL = """
<svg xmlns="http://www.w3.org/2000/svg" width="50" height="50" viewBox="0 0 24 24">
	<path fill="#fff" d="M6 14c-.55 0-1 .45-1 1v3c0 .55.45 1 1 1h3c.55 0 1-.45 1-1s-.45-1-1-1H7v-2c0-.55-.45-1-1-1m0-4c.55 0 1-.45 1-1V7h2c.55 0 1-.45 1-1s-.45-1-1-1H6c-.55 0-1 .45-1 1v3c0 .55.45 1 1 1m11 7h-2c-.55 0-1 .45-1 1s.45 1 1 1h3c.55 0 1-.45 1-1v-3c0-.55-.45-1-1-1s-1 .45-1 1zM14 6c0 .55.45 1 1 1h2v2c0 .55.45 1 1 1s1-.45 1-1V6c0-.55-.45-1-1-1h-3c-.55 0-1 .45-1 1" />
</svg>
"""
SVG_EXIT = """
<svg xmlns="http://www.w3.org/2000/svg" width="50" height="50" viewBox="0 0 24 24">
	<path fill="#fff" d="M6 16h2v2c0 .55.45 1 1 1s1-.45 1-1v-3c0-.55-.45-1-1-1H6c-.55 0-1 .45-1 1s.45 1 1 1m2-8H6c-.55 0-1 .45-1 1s.45 1 1 1h3c.55 0 1-.45 1-1V6c0-.55-.45-1-1-1s-1 .45-1 1zm7 11c.55 0 1-.45 1-1v-2h2c.55 0 1-.45 1-1s-.45-1-1-1h-3c-.55 0-1 .45-1 1v3c0 .55.45 1 1 1m1-11V6c0-.55-.45-1-1-1s-1 .45-1 1v3c0 .55.45 1 1 1h3c.55 0 1-.45 1-1s-.45-1-1-1z" />
</svg>
"""


class SlideShowWidget(QWidget):
    def __init__(self, end_callback = None, full_screen_toggle_callback = None):
        """
        :param end_callback: function to call when the slideshow ends.
        """
        super().__init__()

        self.parent_call_on_stop = end_callback
        self.parent_full_screen_toggle = full_screen_toggle_callback
        

        # Icons
        self.play_icon = self.create_icon_from_svg(SVG_PLAY)
        self.pause_icon = self.create_icon_from_svg(SVG_PAUSE)
        self.full_icon = self.create_icon_from_svg(SVG_FULL)
        self.exit_icon = self.create_icon_from_svg(SVG_EXIT)

        # Parameters
        self.image_files: list = []
        self.loaded_image: QPixmap = QPixmap()
        self.time: int = 0
        self.current_image:int = 0
        self.total_images: int = 0

        self.is_playing = False
        self.is_button_tray_shown = False

        self.button_appear_time = 300


        ##### Timer

        self.timer = QTimer()
        self.timer.setInterval(200) 
        self.timer.timeout.connect(self.update_timer)
        
        self.elapsed_timer = QElapsedTimer()
        self.paused_offset_ms = 0


        ##### --- UI ---
        
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

        layout.addWidget(self.display_label, 0, 0, Qt.AlignmentFlag.AlignCenter)


        # --- Button Tray ---

        overlay = QWidget(self)     
        overlay.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        overlay.setMinimumSize(50, 50)
        overlay.setObjectName("Overlay")
        overlay.setStyleSheet("""
            #Overlay {
                background-color: rgba(0, 0, 0, 0);
                border: none;
                padding: 0px;
            }
        """)
        
        overlay_layout = QGridLayout(overlay)
        overlay_layout.setContentsMargins(5,5,5,5)
        overlay_layout.setColumnStretch(0,1)

        layout.addWidget(overlay, 0, 0)        


        self.button_tray = QWidget(self)
        self.button_tray.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.button_tray.setStyleSheet("""
            QWidget {
                background-color: rgba(0, 0, 0, 50);
                border-radius: 4px;
            }
        """)

        self.button_opacity_effect = QGraphicsOpacityEffect(self.button_tray)
        self.button_tray.setGraphicsEffect(self.button_opacity_effect)


        # Create the animation object, targeting the widget's position (b"pos")
        self.animation = QPropertyAnimation(self.button_opacity_effect, b"opacity")
        self.animation.setDuration(self.button_appear_time) # 300 milliseconds for a quick slide
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad) # Smoother slide


        # Button Layout within the Overlay Container
        button_layout = QHBoxLayout(self.button_tray)
        button_layout.setContentsMargins(10, 10, 10, 10)
        button_layout.setSpacing(2)


        self.btn_back = self.create_icon_button(icon_name = SVG_BACK)
        self.btn_back.clicked.connect(self.skip_bakward_action)
        self.btn_play = self.create_icon_button(icon = self.pause_icon)
        self.btn_play.clicked.connect(self.play_pause_action)
        self.btn_skip = self.create_icon_button(icon_name = SVG_NEXT)
        self.btn_skip.clicked.connect(self.skip_forward_action)
        self.btn_stop = self.create_icon_button(icon_name = SVG_STOP)
        self.btn_stop.clicked.connect(self.stop_slide_show)
        self.btn_hide = self.create_icon_button(icon_name = SVG_DOWN)
        self.btn_hide.clicked.connect(self.hide_button_action)
        self.btn_full = self.create_icon_button(icon = self.exit_icon)
        self.btn_full.clicked.connect(self.full_screen_button_action)

        button_layout.addWidget(self.btn_back)
        button_layout.addWidget(self.btn_play)
        button_layout.addWidget(self.btn_skip)
        button_layout.addWidget(self.btn_stop)
        button_layout.addWidget(self.btn_hide)
        button_layout.addWidget(self.btn_full)


        overlay_layout.addWidget(
            self.button_tray, 
            0, 0, 
            Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter
        )


        self.timer_display = QLabel(self.format_time(self.time))
        self.timer_display.setStyleSheet("""
            QLabel {
                background-color: rgba(0, 0, 0, 50);
                color: white;
                font-weight: bold;
                font-size: 20px;
                border: none;
                border-radius: 15px;
                padding: 5px;
            }
        """
        )
        self.timer_display.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.timer_display.setAlignment(Qt.AlignmentFlag.AlignCenter)

        overlay_layout.addWidget(
            self.timer_display, 
            0, 0, 
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight
        )



    def stop_slide_show(self):

        self.is_button_tray_shown = False
        self.reset_ui()
        self.stop_timer()

        try:
            self.parent_call_on_stop()
        except Exception as e:
            print(f"Error running parent callback on slide stop: {e}")
            return


    def start_slide_show(self, image_files:list, time:int):
        """ Start slideshow from parent window """
        
        self.image_files = image_files
        self.time = int(time) * 1000 + 900 # Convert seconds to miliseconds add a second because it feels better
        self.total_images = len(self.image_files)
        self.current_image = 0
        self.display_new_image()

        QTimer.singleShot(0, self.reset_ui) # using timer to let the UI refresh before reseting
        self.timer_display.setText(self.format_time(self.time))
        
        # Wait 2 seconds and start timer
        QTimer.singleShot(2000, self.start_timer)

        pass


    def start_timer(self):
        """ Starts or resume timer """
        if self.is_playing:
            return

        if self.paused_offset_ms == 0:
            self.elapsed_timer.start()
        else:
            self.elapsed_timer.restart()

        self.timer.start()
        self.is_playing = True
        self.set_play_button_icon()


    def stop_timer(self):
        """ Stops and resets timer """
        if not self.is_playing:
            return
        self.timer.stop()
        self.paused_offset_ms = 0        
        self.elapsed_timer.invalidate()
        self.is_playing = False
        self.set_play_button_icon()
            
    
    def pause_timer(self):
        """ Pause Timer so it can be resumed"""

        if not self.is_playing:
            return


        self.timer.stop()

        self.paused_offset_ms += self.elapsed_timer.elapsed()
        self.is_playing = False
        self.set_play_button_icon()
        
    def restart_timer(self):
        """Resets timer keeps playig status"""

        
        self.timer.stop()
        self.paused_offset_ms = 0
        self.elapsed_timer.invalidate()
        self.elapsed_timer.restart()

        self.update_timer()


        if self.is_playing:
            # Wait 0.5 seconds and start timer
            # QTimer.singleShot(500, self.start_timer)
            self.timer.start()  

        pass
            

    def update_timer(self):
        """Called every 100ms to update the display and check the limit."""
        
        time_since_last_start = self.elapsed_timer.elapsed()
        
        elapsed_ms = self.paused_offset_ms + time_since_last_start

        # Check if the elapsed time has reached or exceeded 3.0 seconds (3000 ms)
        if elapsed_ms >= int(self.time):

            # self.timer.stop()
            self.skip_forward_action()

            pass

        self.timer_display.setText(self.format_time(self.time - elapsed_ms))
        # print(f"{time_since_last_start:04}, {elapsed_ms:04}")


    def format_time(self, total_ms: int) -> str:
        """Converts total milliseconds into MM:SS format."""

        total_ms = max(total_ms, 0)
            
        total_seconds = total_ms // 1000  
        minutes = total_seconds // 60
        seconds = total_seconds % 60        

        return f"{minutes:02}:{seconds:02}"


    def reset_ui(self):
        """ Sets UI to it's current configuration. """
        
        self.set_play_button_icon()
        self.toggle_button_tray(0)

        pass
    

    def hide_button_action(self):
        """ Hide Control Tray on button click """
        self.is_button_tray_shown = False
        self.toggle_button_tray(self.button_appear_time)


    def change_visibility(self):
        self.is_button_tray_shown = not self.is_button_tray_shown


    def toggle_button_tray(self, time:int = 0):
        """ Show or hide the Button overlay based on the control visibility parameter """
        
        self.animation.setDuration(time)

        try:
            self.animation.finished.disconnect()
        except Exception as e:
            pass 
        
        if self.is_button_tray_shown:
            # If True Show Tray
            end_opacity = 1
            self.button_tray.show()
        else:
            # if False Hide Tray    
            end_opacity = 0
            self.animation.finished.connect(self.button_tray.hide)

        self.animation.setStartValue(self.button_opacity_effect.opacity())
        self.animation.setEndValue(end_opacity)

        self.animation.start()
        

    def calculate_widget_bottom(self) -> int:
        """ Calculates the bottom of the widget"""
        
        y = self.height()
        return y


    def play_pause_action(self):
        """Play and Pause the timer on button press"""

        if not self.is_playing:
            self.start_timer()
        else:
            self.pause_timer()
        
        # print(self.is_playing)

        return
    

    def skip_forward_action(self):
        """ Skip Forward on button press"""

        self.current_image += 1        
        # print(self.current_image)
        if self.current_image >= self.total_images:
            self.stop_slide_show()
            return
        
        self.display_new_image()
        self.restart_timer()

    
    def skip_bakward_action(self):
        """ Skip backward on button press"""

        self.current_image -= 1
        # print(self.current_image)
        if self.current_image < 0:
            self.restart_timer()
            self.current_image = 0
            return

        self.display_new_image()

        self.restart_timer()
    


    def full_screen_button_action(self):
        
        try:
            self.parent_full_screen_toggle()
        except Exception as e:
            print(f"Exit FullScreen callback error: {e}")

        pass

    
    def set_full_screen_icon(self, full_screen_mode:bool):
        """
        Set FullScreen icon
        :param full_screen_mode: True = FullScreen, False = Normal
        """
        
        if full_screen_mode:
            icon = self.full_icon
        else:
            icon = self.exit_icon
        self.btn_full.setIcon(icon)
        return


    def set_play_button_icon(self):
        """ Set's play button icon based on if the timer is playing or paused"""
        if self.is_playing:
            icon = self.pause_icon
        else:
            icon = self.play_icon
        self.btn_play.setIcon(icon)
        return


    def create_icon_button(self, icon_name:str = None, icon: QIcon = None, tooltip:str = "", parent = None, size:QSize = QSize(50,50)) -> QPushButton:
        """
        Creates a standard QPushButton with a system stock icon.
        
        :param icon: QStyle.StandardPixmap identifier (e.g., QStyle.SP_MediaSkipForward)
        :param tooltip: The text to show on hover.
        :return: A configured QPushButton instance.
        """
        button = QPushButton(parent)
        button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        button.setStyleSheet("""
            QPushButton:focus {
                outline: 0; 
                border: none
            }
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
        if icon is None:
            try:
                icon = self.create_icon_from_svg(icon_name)
            except:
                icon = QStyle.StandardPixmap.SP_ComputerIcon
                pass

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


    def display_new_image(self):
        self.load_image_file(self.image_files[self.current_image])
        self.update_display_image()

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


    ##### --- Overwriting Functions---

    def resizeEvent(self, event):

        self.update_display_image()
        # print("a")

        return super().resizeEvent(event)
        

    def mousePressEvent(self, event):
        
        # Invert visibility and show or hide the button tray
        self.change_visibility()
        self.toggle_button_tray(self.button_appear_time)        

        return super().mousePressEvent(event)
    
    def keyPressEvent(self, event):

        if event.key() == Qt.Key.Key_Space:
            self.play_pause_action()
        elif event.key() == Qt.Key.Key_Left:
            self.skip_bakward_action()
        elif event.key() == Qt.Key.Key_Right:
            self.skip_forward_action()
        else:
            super().keyPressEvent(event)

    



