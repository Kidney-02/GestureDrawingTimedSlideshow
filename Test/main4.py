from PySide6.QtGui import QPixmap, QPainter, QColor, Qt
from PySide6.QtCore import QSize

def recolor_pixmap_to_white(original_pixmap: QPixmap) -> QPixmap:
    """
    Recolors a monochromatic QPixmap (like a black icon) to white 
    while preserving the original alpha (transparency) channel.
    """
    if original_pixmap.isNull():
        return QPixmap()

    # 1. Setup the new canvas
    size = original_pixmap.size()
    white_pixmap = QPixmap(size)
    white_pixmap.fill(Qt.transparent) # Start with a transparent background

    # 2. Use a QPainter
    painter = QPainter(white_pixmap)
    
    # 3. Set the composition mode to SourceIn
    # This mode ensures that the new color (Source) is drawn ONLY where 
    # the original pixmap (Destination, drawn in step 5) is opaque.
    painter.setCompositionMode(QPainter.CompositionMode_SourceIn) 
    
    # 4. Set the brush (the new color you want) to White
    painter.setBrush(QColor(Qt.white))
    painter.setPen(Qt.NoPen)
    
    # 5. Draw the original pixmap.
    # The SourceIn mode causes the white brush to fill the shape defined 
    # by the original pixmap's opacity.
    painter.drawPixmap(0, 0, original_pixmap)
    
    painter.end()
    
    return white_pixmap

# --- Example Usage ---

# Assuming 'my_black_icon.png' is loaded into a QPixmap instance:
# black_pixmap = QPixmap("path/to/my_black_icon.png")
# white_pixmap = recolor_pixmap_to_white(black_pixmap)
# my_button.setIcon(QIcon(white_pixmap))