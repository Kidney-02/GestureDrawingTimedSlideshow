import random

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QSizePolicy,
    QStackedWidget, QApplication, QGraphicsOpacityEffect,
    QCheckBox
    )

from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import (
    QIntValidator, QDragEnterEvent, QDragLeaveEvent, QDropEvent,
    QIcon
    )

from PreviewZone import *
from Settings import *
from SlideShow import *

ICO_FILE_PATH = "Icon.ico"


class OverlayWidget(QWidget):
    """The widget that will serve as the translucent overlay."""
    def __init__(self, parent=None):
        super().__init__(parent)

        self.default_animation_time = 1000
        
        # Ovrlay presets
        self.color_accept   = "background-color: rgba(76, 175, 80, 0.55); border: 2px dashed rgb(76, 175, 80); border-radius: 4px;"
        self.color_reject   = "background-color: rgba(220, 82, 80, 0.55); border: 2px dashed rgb(220, 82, 80); border-radius: 4px;"
        self.color_finished = "background-color: rgba(0, 0, 0, 0.55); border: 2px dashed rgb(0, 0, 0); border-radius: 4px;"

        self.default_text   = "Drop Image Files Here (PNG, JPG, GIF)"
        self.loading_text   = "Loading..."
        self.warning_text   = "No Images To Show"
        self.finished_text  = "Slideshow Finished"


        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)    

        # Add a message label to the center
        self.label = QLabel(self.default_text)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("color: white; font-size: 24px;")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(2,2,2,2)
        layout.addWidget(self.label)


        # --- FADE EFFECT SETUP ---
        # 1. Create the opacity effect
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        self.animation = QPropertyAnimation(self.opacity_effect, b"opacity")

        self.animation.setDuration(self.default_animation_time) 
        self.animation.setEasingCurve(QEasingCurve.Type.InQuart)
        
        self.start_value = self.opacity_effect.opacity()
        self.animation.setStartValue(self.start_value)
        self.animation.setEndValue(0.0)
        self.animation.finished.connect(self.on_animation_end)  

        # Start hidden
        self.hide() 

    def on_animation_end(self):
        self.hide()
        self.opacity_effect.setOpacity(self.start_value)

    def play_opacity_animation(self, new_time:int = None):

        if new_time is not None:
            self.animation.setDuration(new_time)
        else:
            self.animation.setDuration(self.default_animation_time)

        self.animation.stop()
        self.animation.start()


    def show(self, state:int = 1):
        """
        0 : "Accept Files",
        1 : "Reject Files",
        2 : "No Images",
        3 : "Loading Images"
        4 : "Finished"
        """
        self.animation.stop()
        self.on_animation_end()

        if state == 0:
            self.setStyleSheet(self.color_accept)
            self.label.setText(self.default_text)
        elif state == 1:
            self.setStyleSheet(self.color_reject)
            self.label.setText(self.default_text)
        elif state == 2:
            self.setStyleSheet(self.color_reject)
            self.label.setText(self.warning_text)
        elif state == 3:
            self.setStyleSheet(self.color_accept)
            self.label.setText(self.loading_text)
        elif state == 4:
            self.setStyleSheet(self.color_finished)
            self.label.setText(self.finished_text)

        # self.update_geometry()
        super().show()

    def update_opacity(self):
        # print(self.styleSheet())
        return

    def resizeEvent(self, event):
        # self.update_geometry()
        return super().resizeEvent(event)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Drawing Practicer")
        self.setWindowIcon(QIcon(ICO_FILE_PATH))
        self.setAcceptDrops(True)

        # Slideshow Settings
        self.count:int = 10
        self.time:int = 10
        self.full_screen:bool = True
        self.thumbnail_size:int = 200 

        ### Store file paths and cache thumbnails ###
        self.image_files:list = []
        self.image_cache:dict = {} # caches thumbnail for preview
        
        # --- QSettings setup ---
        self.settings = Settings()
        self.load_settings()

        validator = QIntValidator(1, 100)

        ##### --- Stacked Widget ---

        self.stacked_widget = QStackedWidget()
        # stacked_layout = QVBoxLayout(self.stacked_widget)
        # self.stacked_widget.layout
        # setContentsMargins(0, 0, 0, 0)
        self.setCentralWidget(self.stacked_widget)
        
        ##### --- Top Widget ---

        # Used to store main menu and overlay in the same spot
        top_widget = QWidget()
        top_layout = QGridLayout(top_widget)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(0)

        ##### --- Main Manu ---

        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)        
        main_layout.setContentsMargins(0, 0, 0, 0) 
        

        ##### --- Section 1: Slideshow Controls ---

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

        # FullScreen Checkbox
        self.full_screen_checkbox = QCheckBox("Start in FullScreen")
        self.full_screen_checkbox.setChecked(self.full_screen)
        self.full_screen_checkbox.stateChanged.connect(self.calc_full_screen_check)
        control_layout.addWidget(self.full_screen_checkbox)

        # Start Button
        self.start_button = QPushButton("Start Session")
        self.start_button.setFixedWidth(100)
        self.start_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.start_button.setCursor(Qt.PointingHandCursor)   
        self.start_button.clicked.connect(self.start_slide_show)
        self.start_button.setStyleSheet("""
            QPushButton {
                color: white;
                font-weight: bold;
                border: none;
                border-radius: 4px;
                padding: 3px;
            }
            QPushButton {
                background-color: #4CAF50; 
            }
            QPushButton:hover {
                background-color: #66BB6A;
            }    
            QPushButton:pressed {
                background-color: #388E3C;
            }                                        
        """
        )
        control_layout.addWidget(self.start_button)
        
        control_layout.addStretch(1)

        

        main_layout.addWidget(control_group)
        main_layout.addWidget(self.create_separator())

        ##### --- Section 2: Image Preview Zone ---
             
        self.preview_zone = PreviewZone(self.thumbnail_size)        
        self.preview_zone.set_image_files(self.image_cache)
        self.preview_zone.get_item_width()
        # self.preview_zone.set_thumbail_size(self.thumbnail_size)
               

        main_layout.addWidget(self.preview_zone)


        preview_control_group = QWidget()
        preview_control_layout = QHBoxLayout(preview_control_group)
        preview_control_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        preview_control_layout.addStretch(1)
        preview_control_layout.setSpacing(10)
        
        
        # Image Count
        self.count_label = QLabel()
        self.update_image_count() 
        preview_control_layout.addWidget(self.count_label)

        # Clear Button
        self.clear_button = QPushButton("Clear Images")
        self.clear_button.setFixedWidth(100)
        self.clear_button.setCursor(Qt.PointingHandCursor)
        self.start_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.clear_button.setMaximumWidth(100)
        self.clear_button.clicked.connect(self.clear_image_files)
        self.clear_button.setStyleSheet("""
            QPushButton {
                color: white;
                font-weight: bold;
                border: none;
                border-radius: 4px;
                padding: 3px;
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
        preview_control_layout.addWidget(self.clear_button)


        main_layout.addWidget(preview_control_group)


        ##### --- Slide Show ---
        self.slide_show = SlideShowWidget(
            end_callback = self.end_slide_show,
            full_screen_toggle_callback = self.full_screen_toggle
            )
        self.slide_show.hide()


        ##### --- The Overlay ---
        self.overlay = OverlayWidget(self)
        self.overlay.hide() # Set overlay hidden on Start

        # Overlay with grid Layout
        top_layout.addWidget(main_widget, 0, 0)
        top_layout.addWidget(self.overlay, 0, 0)

        self.stacked_widget.addWidget(top_widget)
        self.stacked_widget.addWidget(self.slide_show)


    def calc_time_and_count(self):

        self.count = self.count_input.text()
        self.time = self.time_input.text()


        return
        

    def start_slide_show(self):

        if not self.image_files:
            self.overlay.show(2)
            self.overlay.play_opacity_animation()
            
            return
        else:
            self.calc_time_and_count()
            self.calc_full_screen_check()

            self.stacked_widget.setCurrentIndex(1)
            self.slide_show.show()
            if self.full_screen:
                self.showFullScreen()
            self.slide_show.set_full_screen_icon(not self.full_screen)
            self.slide_show.start_slide_show(self.get_slide_show_images(), self.time)

            

            # QApplication.processEvents()

        pass


    def end_slide_show(self):
        self.stacked_widget.setCurrentIndex(0)
        self.slide_show.hide()
        self.overlay.show(4)
        self.overlay.play_opacity_animation()

        # Pop Up overlay here


    def get_slide_show_images(self) -> list:
        
        if not self.image_files:
            return
        
        # sample = self.image_files.copy()

        sample = random.sample(self.image_files.copy(), min(int(self.count), len(self.image_files)))
        # print(sample)
        # print(f"\033[31m{len(self.image_files)}\033[0m")
        # print(f"\033[32m{len(sample)}\033[0m")
        random.shuffle(sample)
        # print(sample)
        # print(f"\033[33m{sample}\033[0m")
        return sample


    def calc_full_screen_check(self):
        self.full_screen = self.full_screen_checkbox.isChecked()

        return    


    def load_image_thumbnails(self):

        image_thumbnails = []
        for file_path in self.image_files:
            try:
                img = Image.open(file_path)
                img.thumbnail((400,400))
                image_thumbnails.append(img)
            except Exception as e:
                print(f"Error loading image {file_path}: {e}")
            

        # print(image_thumbnails)
        return image_thumbnails


    def clear_image_files(self):
        self.image_files.clear()
        self.image_cache.clear()
        self.preview_zone.clear_image_files()
        self.update_image_count()
        pass
        

    def create_separator(self):
        """Utility to create a horizontal rule for visual separation."""
        separator = QWidget()
        separator.setFixedHeight(1)
        separator.setStyleSheet("background-color: #ccc;")
        return separator
    

    def update_image_count(self):
        self.count_label.setText(f"{str(len(self.image_files))} total images") 

    
    def full_screen_toggle(self):
        if self.isFullScreen():
            self.showNormal()
            self.slide_show.set_full_screen_icon(True)
        else:
            self.showFullScreen()
            self.slide_show.set_full_screen_icon(False)


    def load_settings(self):
        """Loads window geometry count and time from QSettings."""
        
        settings = self.settings.settings_load()

        # print(settings)

        if settings is not None:
            try: self.restoreGeometry(settings.value("geometry"))
            except: pass

            self.count = settings.value("count", 10, type=int)

            self.time = settings.value("time", 10, type=int)

            self.image_files = settings.value("images", [])
            # print(f"\033[31m{self.image_files}\033[0m")

            self.image_cache = self.load_image_thumbnails()
            # print(f"\033[34m{self.image_cache}\033[0m")

            self.thumbnail_size = settings.value("image_size", 200, type=int)
 
            self.full_screen = settings.value("fullscreen", True, type=bool)
            # print(self.full_screen)


        else:
            self.count = 10
            self.time = 30
            self.image_files = []
            self.thumbnail_size = 200
            self.full_screen = True

    ##### --- Overwrite Functions ---

    def closeEvent(self, event):
        """Saves window geometry to QSettings and closes the secondary window."""

        self.showNormal()
        self.calc_time_and_count()
        self.calc_full_screen_check()

        settings = {
            "geometry": self.saveGeometry(),
            "count": self.count_input.text(),
            "time": self.time_input.text(),
            "fullscreen": self.full_screen,
            # "image_size": self.preview_zone.thumbnail_size
        }
        if not self.image_files:
            settings.update({"images": []})
        else :
            settings.update({"images": self.image_files})

        if not self.preview_zone.thumbnail_size:
            settings.update({"image_size": 200})
        else :
            settings.update({"image_size": self.preview_zone.thumbnail_size})

        self.settings.settings_save(settings)

        event.accept()


    def dragEnterEvent(self, event: QDragEnterEvent):
        """Accepts the drag if it contains acceptable file paths (URIs)."""
        if event.mimeData().hasUrls():
            can_accept = any(
                url.isLocalFile() and url.toLocalFile().lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))
                for url in event.mimeData().urls()
            )
            
            if can_accept:
                event.acceptProposedAction()

            else:
                event.ignore()
            
            # for show True = 1, False = 0
            self.overlay.show(1 - int(can_accept))
            self.overlay.raise_()
        else:
            event.ignore()


    def dragLeaveEvent(self, event: QDragLeaveEvent):
        # Hide the overlay
        self.overlay.hide()
        super().dragLeaveEvent(event)
        

    def dropEvent(self, event):
        """Handles the actual drop operation by storing paths and triggering redrawing."""

        self.overlay.show(3)
        QApplication.processEvents()


        # Add to the image list and cache thumbnails
        for url in event.mimeData().urls():
            if url.isLocalFile() and url.toLocalFile().lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                file_path = url.toLocalFile()
                if file_path not in self.image_files:
                    self.image_files.append(file_path)


        # Reset instruction label style
        self.overlay.hide()

        self.preview_zone.set_image_files(self.load_image_thumbnails())
        self.update_image_count()

        event.acceptProposedAction()

        return super().dropEvent(event)


    def resizeEvent(self, event):

        # self.overlay.resizeEvent(event)
        # self.slide_show.resizeEvent(event)
        return super().resizeEvent(event)
    

    def keyPressEvent(self, event):

        if event.key() == Qt.Key.Key_Escape:
            self.showNormal()
            self.slide_show.set_full_screen_icon(True)
        else:
            super().keyPressEvent(event)


        return
