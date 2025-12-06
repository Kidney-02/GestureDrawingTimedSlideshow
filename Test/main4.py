import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel,
    QMainWindow
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPalette, QColor

class ScalingWidget(QWidget):
    """
    A custom QWidget that demonstrates scaling behavior.
    The content (self.label) fills the entire widget space.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 1. Set up the internal layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0) # Remove margins so label fills space
        self.layout.setSpacing(0)
        
        # 2. Create the content widget (QLabel)
        self.label = QLabel("I scale to fit my parent!")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Apply style for visual clarity
        palette = self.label.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor("#3498db")) # Blue background
        palette.setColor(QPalette.ColorRole.WindowText, QColor("white"))
        self.label.setAutoFillBackground(True)
        self.label.setPalette(palette)
        
        self.layout.addWidget(self.label)
        
        # 3. Crucial step: Ensure the widget has NO fixed size constraints
        # By default, a QWidget without fixed constraints will expand in a layout.
        # We ensure no minimum size is enforced that would prevent shrinking.
        # self.setMinimumSize(0, 0) # This is usually the default, but good to know.
        
        # Optionally, set a size policy to strongly encourage expansion
        self.setSizePolicy(
            self.sizePolicy().expanding,
            self.sizePolicy().expanding
        )


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Scaling Widget Demo")
        self.setGeometry(100, 100, 600, 400)

        # 1. Create the container/central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 2. Use a main layout to manage the custom widget
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10) # Padding around the custom widget

        # 3. Instantiate the custom scaling widget
        self.scaling_widget = ScalingWidget()
        
        # 4. Add the scaling widget to the layout
        # The QVBoxLayout will automatically resize the scaling_widget to fill 
        # the available space of the central_widget.
        main_layout.addWidget(self.scaling_widget)
        
        # Add a reference label at the bottom to show the scaling widget's flexibility
        ref_label = QLabel("Resize the window to see the blue widget scale.")
        ref_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(ref_label)


# Note: The original prompt uses QMainWindow, so ensure it's imported.
from PyQt6.QtWidgets import QMainWindow 
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())