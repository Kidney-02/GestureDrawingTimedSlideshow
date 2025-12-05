import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame
)
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QRect, QPoint
from PySide6.QtGui import QFont

class SlidingOverlayWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Countdown and Sliding Overlay")
        self.setGeometry(100, 100, 800, 600)

        # 1. Setup Main Layout and Central Widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # QLayout for background and countdown (widgets that flow)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # 2. Background Label
        self.background_label = QLabel("Click the window to toggle the overlay visibility!")
        self.background_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.background_label.setStyleSheet("background-color: #34495e; color: white; font-size: 24px;")
        self.main_layout.addWidget(self.background_label)

        # 3. Countdown Label (Top)
        self.countdown_label = QLabel("10")
        self.countdown_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont("Arial", 48)
        font.setBold(True)
        self.countdown_label.setFont(font)
        self.countdown_label.setStyleSheet("color: #ecf0f1; background-color: rgba(0, 0, 0, 0.4); padding: 10px;")
        self.main_layout.setStretch(0, 1)
        self.main_layout.addWidget(self.countdown_label, alignment=Qt.AlignmentFlag.AlignTop)


        # 4. Sliding Overlay Container (Absolute Position)
        self.overlay_widget = QFrame(self.central_widget) 
        self.overlay_height = 80
        self.overlay_widget.setFixedHeight(self.overlay_height)
        self.overlay_widget.setStyleSheet("background-color: #2c3e50;")
        
        overlay_layout = QHBoxLayout(self.overlay_widget)
        overlay_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Button inside the overlay
        self.overlay_button = QPushButton("Action Button")
        self.overlay_button.setStyleSheet(
            "QPushButton { background-color: #e74c3c; color: white; border: none; padding: 10px 20px; font-size: 18px; border-radius: 5px; }"
            "QPushButton:hover { background-color: #c0392b; }"
        )
        self.overlay_button.clicked.connect(self.button_action)
        overlay_layout.addWidget(self.overlay_button)
        
        self.overlay_is_visible = True
        
        # 5. Animation Setup
        self.animation = QPropertyAnimation(self.overlay_widget, b"pos")
        self.animation.setDuration(300)
        self.animation.setEasingCurve(QEasingCurve.Type.OutQuad)
        
        # 6. Countdown Timer Setup
        self.countdown_value = 10
        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.update_countdown)
        self.timer.start()
        
        # Initialize position
        self.overlay_widget.move(0, self.height() - self.overlay_height)

    
    def resizeEvent(self, event):
        """Ensures absolutely positioned overlay stays anchored to the bottom."""
        super().resizeEvent(event)
        
        self.countdown_label.setGeometry(QRect(0, 0, self.width(), self.countdown_label.height()))
        
        # Recalculate overlay position based on visibility and window size
        if self.overlay_is_visible:
            y_pos = self.height() - self.overlay_height
        else:
            y_pos = self.height() # Fully hidden
            
        self.overlay_widget.setGeometry(QRect(0, y_pos, self.width(), self.overlay_height))


    def mousePressEvent(self, event):
        """
        Toggles the overlay visibility when the window is clicked.
        If visible, it hides (slides down).
        If hidden, it shows (slides up).
        """
        if event.button() == Qt.MouseButton.LeftButton:
            # Check the current state and set the opposite action
            if self.overlay_is_visible:
                # Is visible -> Hide (slide down)
                self.toggle_overlay(show=False)
            else:
                # Is hidden -> Show (slide up)
                self.toggle_overlay(show=True)
        super().mousePressEvent(event)
        
        
    def toggle_overlay(self, show: bool):
        """Slides the overlay up (show=True) or down (show=False)."""
        
        if show == self.overlay_is_visible:
            return # Already in the desired state, stop to avoid re-running animation
        
        # Calculate destination Y position
        if show:
            # Slide Up (Show): End position is sitting on the bottom
            end_y = self.height() - self.overlay_height 
        else:
            # Slide Down (Hide): End position is just below the window edge
            end_y = self.height() 

        self.overlay_is_visible = show # Update state
        
        # Set up and start the animation
        self.animation.setStartValue(self.overlay_widget.pos())
        self.animation.setEndValue(QPoint(0, end_y))
        self.animation.start()

    def update_countdown(self):
        """Updates the countdown label every second, without affecting overlay visibility."""
        if self.countdown_value > 0:
            self.countdown_value -= 1
            self.countdown_label.setText(str(self.countdown_value))
        else:
            self.timer.stop()
            self.countdown_label.setText("TIME UP!")
            self.countdown_label.setStyleSheet("color: #e74c3c; background-color: rgba(0, 0, 0, 0.4); padding: 10px;")


    def button_action(self):
        """Action when the overlay button is clicked (also hides it)."""
        print("Action Button Clicked!")
        self.background_label.setText("Action Button Was Clicked! Overlay is sliding down.")
        # When button is clicked, we explicitly want it to hide (slide down)
        self.toggle_overlay(show=False) 

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SlidingOverlayWindow()
    window.show()
    sys.exit(app.exec())