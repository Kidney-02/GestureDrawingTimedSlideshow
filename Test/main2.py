from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QTextEdit, QLabel
)
from PySide6.QtGui import QWheelEvent
import sys

# 1. Custom Parent Widget to intercept the event
class EventInterceptingWidget(QWidget):
    """A QWidget that intercepts wheel events and does not pass them to children."""
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Setup layout and a child widget that we want to prevent from scrolling
        layout = QVBoxLayout(self)
        
        self.label = QLabel("Parent Widget (Intercepts Scroll)", self)
        layout.addWidget(self.label)
        
        # This child widget normally scrolls, but won't here.
        self.child_text_edit = QTextEdit(self)
        self.child_text_edit.setText("Try scrolling over this text. " * 50)
        layout.addWidget(self.child_text_edit)
        
        self.setLayout(layout)

    # 2. Override the specific event handler (wheelEvent)
    def wheelEvent(self, event: QWheelEvent):
        """
        Reimplement this method to capture the scroll event.
        """
        # --- THE KEY LINE ---
        # Call event.accept() to mark the event as handled. 
        # The QWidget framework will stop propagating it to child widgets.
        event.accept()
        
        # OPTIONAL: Add custom logic for the parent widget if needed
        # print("Wheel event intercepted by the parent!")
        
        # If you called event.ignore(), the event would continue propagating 
        # to the parent's parent, not the children.

# 3. Application Setup
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Create an instance of our custom widget
    main_window = EventInterceptingWidget()
    main_window.setWindowTitle("Event Propagation Stopped Example")
    main_window.resize(300, 400)
    main_window.show()
    
    sys.exit(app.exec())