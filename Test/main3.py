import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QGridLayout, QLabel, 
    QPushButton, QMainWindow, QSizePolicy
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPalette, QColor

class ScalingWidget(QWidget):
    """
    The custom widget that scales to fill its parent.
    It uses an internal QGridLayout where rows/columns are configured to expand 
    around fixed-size children.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Apply style for visual clarity of the container
        self.setStyleSheet("background-color: #3498db; border: 2px solid #2980b9;")
        
        # --- External Scaling Setup (Crucial) ---
        # 1. Ensure the ScalingWidget itself requests to expand
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )
        
        # --- Internal Layout Setup ---
        main_v_layout = QVBoxLayout(self)
        main_v_layout.setContentsMargins(10, 10, 10, 10) 
        main_v_layout.setSpacing(0)
        
        # 2. Create the INTERNAL QGridLayout
        internal_grid = QGridLayout()
        internal_grid.setSpacing(10)
        
        # 3. Create fixed-size content widgets
        
        # Widget A: A Simple QLabel (Expanding in this version)
        info_label = QLabel("Internal Information Panel (Main Content)")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_label.setStyleSheet("background-color: #f39c12; color: white; padding: 5px;")
        # Allow the main info panel to expand
        info_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        # Widget B: A fixed-height QPushButton
        action_button = QPushButton("Internal Action (Fixed Height)")
        action_button.setStyleSheet("background-color: #27ae60; color: white; padding: 10px;")
        action_button.setFixedHeight(40) # Fixed Height
        
        # Widget C: A fixed-size dummy label
        dummy_label = QLabel("Fixed Size Corner")
        dummy_label.setStyleSheet("background-color: #bdc3c7; color: #2c3e50; padding: 5px;")
        dummy_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        dummy_label.setFixedSize(120, 40) # Fixed Size
        
        # 4. Add the widgets to the internal grid
        
        # Row 0: Main expanding content (takes up all rows and column 0)
        internal_grid.addWidget(info_label, 0, 0, 2, 1) 
        
        # Row 0, Column 1: Fixed Corner (top right)
        internal_grid.addWidget(dummy_label, 0, 1) 
        
        # Row 1, Column 1: Fixed Button (bottom right)
        internal_grid.addWidget(action_button, 1, 1)
        

        # --- CRITICAL FIX: Set Stretch Factors for the Internal Grid ---
        
        # 5. Set Stretch Factors for the internal grid
        # The goal is to make the entire grid expand.
        
        # Give column 0 stretch (where the expanding info_label is)
        internal_grid.setColumnStretch(0, 1) 
        # Give column 1 minimum stretch (fixed widgets are here)
        internal_grid.setColumnStretch(1, 0)
        
        # Since Row 0 and Row 1 both contain fixed-height items in column 1, 
        # we need to ensure that when the grid grows vertically, the extra space 
        # is distributed across the rows that contain the expanding content.
        
        # If we want the rows to expand evenly, use setRowStretch(row, 1) for both.
        # If we want all vertical space to go to row 0 (where the main label is), use:
        internal_grid.setRowStretch(0, 1)  # Row 0 gets all expansion space
        internal_grid.setRowStretch(1, 0)  # Row 1 has fixed elements, so no stretch needed
        
        # 6. Add the internal grid layout to the main_v_layout
        main_v_layout.addLayout(internal_grid)
        

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fixed Contents in Scaling Grid Demo")
        self.setGeometry(100, 100, 700, 500)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Outer Grid Layout
        main_grid_layout = QGridLayout(central_widget)
        main_grid_layout.setContentsMargins(10, 10, 10, 10)
        main_grid_layout.setSpacing(10)

        # Create the custom scaling widget (now with an internal grid)
        self.scaling_widget = ScalingWidget()
        
        # Other context widgets
        corner_widget = QLabel("Fixed Top Right")
        corner_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        corner_widget.setStyleSheet("background-color: #e74c3c; color: white;")
        corner_widget.setFixedSize(150, 50)
        
        bottom_widget = QLabel("Footer Panel")
        bottom_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        bottom_widget.setStyleSheet("background-color: #9b59b6; color: white;")
        bottom_widget.setFixedHeight(40)


        # --- Place Widgets in the Outer Grid ---
        main_grid_layout.addWidget(self.scaling_widget, 0, 0) # Primary Scaling Widget
        main_grid_layout.addWidget(corner_widget, 0, 1)        # Fixed Corner
        main_grid_layout.addWidget(bottom_widget, 1, 0, 1, 2)  # Footer

        # --- Stretch Factors for the Outer Grid (Ensures the WHOLE blue widget scales) ---
        main_grid_layout.setColumnStretch(0, 1) 
        main_grid_layout.setColumnStretch(1, 0)

        main_grid_layout.setRowStretch(0, 1)     
        main_grid_layout.setRowStretch(1, 0)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())