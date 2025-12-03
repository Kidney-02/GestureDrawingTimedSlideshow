import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, 
    QHBoxLayout, QLabel, QPushButton, QSizePolicy, 
    QGridLayout, QGraphicsOpacityEffect  # <-- Added for fade effect
)
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve # <-- Added for smooth animation

class OverlayWidget(QMainWindow):
    """
    A QMainWindow containing a QLabel (bottom layer) and an overlaid QWidget 
    with three buttons (top layer) centered at the bottom. 
    The button container now fades in and out.
    """
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Layered Widget with Hideable Overlay")
        self.setGeometry(100, 100, 600, 450)
        
        # --- Base Container Setup ---
        self.main_container = QWidget()
        self.setCentralWidget(self.main_container)
        
        # QGridLayout allows stacking (layering) widgets in the same cell.
        self.layout = QGridLayout(self.main_container)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        # --- 1. Bottom Layer (The Label) ---
        self.background_label = QLabel("Bottom Layer: Main Content Area")
        self.background_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.background_label.setStyleSheet("""
            QLabel {
                background-color: #ECEFF1; /* Light Gray */
                font-size: 24px;
                color: #546E7A;
                border: 2px dashed #B0BEC5;
            }
        """)
        # The background label goes into cell (0, 0)
        self.layout.addWidget(self.background_label, 0, 0)
        
        # --- 2. Top Layer (The Button Container) ---
        
        self.button_overlay_container = QWidget()
        self.button_overlay_container.setStyleSheet("""
            QWidget {
                /* Semi-transparent black background: 0, 0, 0 (black) with 80 (alpha) */
                background-color: rgba(0, 0, 0, 80); 
                border-radius: 12px;
                padding: 10px;
            }
        """)

        # --- FADE EFFECT SETUP ---
        # 1. Create the opacity effect
        self.opacity_effect = QGraphicsOpacityEffect(self.button_overlay_container)
        self.button_overlay_container.setGraphicsEffect(self.opacity_effect)
        
        # 2. Create the animation object
        self.animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.animation.setDuration(300) # 300 milliseconds for a quick fade
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad)

        # Button Layout within the Overlay Container
        button_layout = QHBoxLayout(self.button_overlay_container)
        button_layout.setContentsMargins(10, 10, 10, 10)
        button_layout.setSpacing(15)
        
        # Create and add the three buttons
        self.btn1 = self._create_styled_button("Action 1", "#FF9800") # Orange
        self.btn2 = self._create_styled_button("Action 2", "#2196F3") # Blue
        # This button will now trigger the fade out
        self.btn3 = self._create_styled_button("Hide Overlay", "#F44336") # Red
        
        # --- Connect the hide action ---
        self.btn3.clicked.connect(self.hide_overlay_box)

        button_layout.addWidget(self.btn1)
        button_layout.addWidget(self.btn2)
        button_layout.addWidget(self.btn3)
        
        # Final Placement of the Overlay at the bottom center
        self.layout.addWidget(
            self.button_overlay_container, 
            0, 0, 
            Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter
        )
        
        # --- 3. Add a Recovery/Show Button (Outside the Overlay) ---
        
        # We need a way to bring the overlay back. We'll use a standard
        # layout within the background label (which acts as a container)
        self.show_btn = QPushButton("Show Overlay")
        self.show_btn.setStyleSheet("""
            QPushButton {
                background-color: #795548; /* Brown */
                color: white;
                border-radius: 4px;
                padding: 5px;
            }
        """)
        self.show_btn.setFixedSize(120, 30)
        self.show_btn.clicked.connect(self.show_overlay_box)
        self.show_btn.hide() # Start hidden
        
        # Use a QVBoxLayout inside the QLabel to hold the Show button at the top
        label_layout = QVBoxLayout(self.background_label)
        label_layout.addWidget(self.show_btn, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)
        
        self.background_label.setLayout(label_layout)
        
        # Ensure the background label expands to fill the entire space
        self.background_label.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        
        self.main_container.setLayout(self.layout)

    def _create_styled_button(self, text: str, color: str) -> QPushButton:
        """Helper function to create a consistently styled button."""
        button = QPushButton(text)
        button.setFixedSize(110, 40)
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {color}; 
                color: white;
                font-weight: bold;
                border: none;
                border-radius: 6px;
                padding: 8px;
            }}
            QPushButton:hover {{
                background-color: {color.replace('#', '') + 'AA'}; /* Slightly lighter hover */
            }}
            QPushButton:pressed {{
                background-color: {color.replace('#', '') + '88'}; /* Slightly darker pressed */
            }}
        """)
        return button
    
    def hide_overlay_box(self):
        """Fades out the semi-transparent button container."""
        # Setup fade out animation (1.0 -> 0.0)
        self.animation.stop() # Stop any active animation
        self.animation.setStartValue(self.opacity_effect.opacity())
        self.animation.setEndValue(0.0)

        # Disconnect any previous connections from show_overlay_box
        try:
            self.animation.finished.disconnect()
        except TypeError:
            pass

        # Connect a lambda function to hide the widget only after the animation is done
        self.animation.finished.connect(lambda: (
            self.button_overlay_container.hide(), 
            self.show_btn.show(),
            self.animation.finished.disconnect() # Clean up connection
        ))
        
        self.animation.start()
        
    def show_overlay_box(self):
        """Fades in the semi-transparent button container."""
        
        # 1. Make sure the container is visible (it must be visible to animate)
        self.button_overlay_container.show()
        self.show_btn.hide()

        # 2. Setup fade in animation (0.0 -> 1.0)
        self.animation.stop() # Stop any active animation
        
        # Ensure it starts from 0.0 (in case the previous animation was interrupted)
        self.opacity_effect.setOpacity(0.0) 
        
        self.animation.setStartValue(0.0)
        self.animation.setEndValue(1.0)
        
        # Disconnect any lingering hide connections
        try:
            self.animation.finished.disconnect()
        except TypeError:
            pass 
        
        self.animation.start()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = OverlayWidget()
    window.show()
    sys.exit(app.exec())