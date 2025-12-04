import sys
import re # We'll use the regex module for string replacement
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QPushButton
)
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtCore import QByteArray, QSize, Qt

# The base SVG content. The width/height attributes will be dynamically modified.
SVG_CONTENT_TEMPLATE = """
<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 24 24">
    <path fill="#FFFFFF" d="m11.565 13.873l-2.677-2.677q-.055-.055-.093-.129q-.037-.073-.037-.157q0-.168.11-.289q.112-.121.294-.121h5.677q.181 0 .292.124t.111.288q0 .042-.13.284l-2.677 2.677q-.093.093-.2.143t-.235.05t-.235-.05t-.2-.143"/>
</svg>
"""

class MainWindow(QMainWindow):
    """
    Main window for the PySide application.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PySide SVG Icon Demo (Dynamic Size)")
        self.setGeometry(100, 100, 350, 200)

        # Setting up a simple dark theme for better visibility of the white icon
        self.setStyleSheet("""
            QMainWindow { background-color: #f0f0f0; }
            QPushButton {
                background-color: #0078D4; /* Windows Blue */
                color: white;
                border: none;
                padding: 10px 20px;
                font-size: 16px;
                border-radius: 8px;
            }
            QPushButton:hover { background-color: #005A9E; }
            QPushButton:pressed { background-color: #004578; }
        """)

        # --- Setup Central Widget and Layout ---
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # --- 1. Create the QIcon from SVG with a specific rendering size ---
        # We want the QPixmap to be rendered at 64x64 for maximum sharpness, 
        # even if the button only shows it at 24x24.
        svg_render_size = QSize(64, 64) 
        custom_icon = self.create_icon_from_svg(SVG_CONTENT_TEMPLATE, svg_render_size)

        # --- 2. Create the QPushButton ---
        self.button = QPushButton("Run Action")
        self.button.setToolTip(f"Icon rendered at {svg_render_size.width()}x{svg_render_size.height()}px")
        
        # Set the icon and its display size (smaller than the render size for scaling test)
        self.button.setIcon(custom_icon)
        self.button.setIconSize(QSize(24, 24))

        self.button.clicked.connect(self.on_button_click)
        layout.addWidget(self.button)

    def set_svg_size(self, svg_template: str, size: QSize) -> str:
        """
        Inserts the desired width and height into the SVG template string.
        """
        # Using string formatting to inject the size values into the template
        return svg_template.format(width=size.width(), height=size.height())


    def create_icon_from_svg(self, svg_template: str, render_size: QSize) -> QIcon:
        """
        Creates a QIcon object after setting the size in the SVG content string.
        """
        # 1. Update the SVG string with the desired rendering size
        sized_svg_data = self.set_svg_size(svg_template, render_size)

        # 2. Convert to QByteArray
        svg_byte_array = QByteArray(sized_svg_data.encode('utf-8'))
        pixmap = QPixmap()
        
        # 3. Load the data (Qt now knows the exact render size from the string attributes)
        if pixmap.loadFromData(svg_byte_array, "SVG"):
            # The QIcon is created from the high-resolution QPixmap
            return QIcon(pixmap)
        else:
            print("Error: Could not load SVG data.")
            return QIcon()

    def on_button_click(self):
        """
        A simple function to run when the button is clicked.
        """
        print("--- Action Triggered! ---")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())