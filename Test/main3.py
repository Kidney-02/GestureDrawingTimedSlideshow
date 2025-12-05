import sys
from PySide6.QtWidgets import QApplication, QWidget, QPushButton
from PySide6.QtCore import QPoint

class ManualPositionWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Manual Positioning")
        self.setGeometry(100, 100, 500, 400) # Initial window size and position
        
        # We need to disable the default layout management to place widgets manually
        self.setLayout(None) 
        
        # 1. Create the button
        self.button = QPushButton("Manual Positioned Button", self)
        self.button.setFixedSize(200, 50) # Set a fixed size

        # 2. Set the position using move(x, y)
        self.button.move(50, 50) 
        
        # 3. Alternatively, using QPoint
        self.label = QPushButton("Moved with QPoint", self)
        self.label.move(QPoint(280, 200)) # Sets the top-left corner to (280, 200)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ManualPositionWindow()
    window.show()
    sys.exit(app.exec())