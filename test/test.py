import sys
import os
import requests
import urllib.parse
from bs4 import BeautifulSoup
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QWidget, QApplication, QLabel, QVBoxLayout, QScrollArea

class ImageDownloader(QThread):
    finished = Signal(str)
    error = Signal(str)

    def __init__(self, url):
        super().__init__()
        self.url = url

    def run(self):
        # Professional Browser Headers
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

        try:
            target_url = self.url

            # --- CASE 1: Pinterest ---
            if "pinterest.com/pin/" in target_url:
                headers["Referer"] = "https://www.pinterest.com/"
                res = requests.get(target_url, headers=headers, timeout=10)
                soup = BeautifulSoup(res.text, 'html.parser')
                og_tag = soup.find("meta", property="og:image")
                if og_tag:
                    # Upgrade to highest resolution
                    target_url = og_tag["content"].replace("/736x/", "/originals/")

            # --- CASE 2: Google Images ---
            # Google URLs often look like: https://www.google.com/imgres?imgurl=http://site.com/pic.jpg&imgrefurl=...
            elif "google.com/imgres" in target_url or "google.com/imgurl" in target_url:
                parsed = urllib.parse.urlparse(target_url)
                params = urllib.parse.parse_qs(parsed.query)
                if 'imgurl' in params:
                    target_url = params['imgurl'][0]
            

            # --- DOWNLOAD STAGE ---
            img_res = requests.get(target_url, headers=headers, stream=True, timeout=15)
            img_res.raise_for_status()

            content_type = img_res.headers.get('Content-Type', '').lower()
            ext = content_type.split('/')[-1] if 'image/' in content_type else 'jpg'
            
            save_path = os.path.abspath(f"grabbed_image_{hash(target_url)}.{ext}")
            
            with open(save_path, 'wb') as f:
                for chunk in img_res.iter_content(chunk_size=8192):
                    f.write(chunk)

            self.finished.emit(save_path)

        except Exception as e:
            self.error.emit(str(e))

class PureRefLite(QWidget):
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.setWindowTitle("Universal Image Grabber")
        self.resize(500, 400)

        # UI Setup
        self.label = QLabel("Drag Google or Pinterest links here")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("font-size: 16px; font-weight: bold; color: #666;")
        
        self.image_display = QLabel("No Image Loaded")
        self.image_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_display.setScaledContents(True)

        layout = QVBoxLayout(self)
        layout.addWidget(self.label)
        layout.addWidget(self.image_display)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        url = event.mimeData().urls()[0].toString()
        self.label.setText("Processing URL...")
        
        self.downloader = ImageDownloader(url)
        self.downloader.finished.connect(self.display_image)
        self.downloader.error.connect(self.handle_error)
        self.downloader.start()

    def display_image(self, path):
        self.label.setText(f"Loaded: {os.path.basename(path)}")
        pixmap = QPixmap(path)
        # Scale for display while keeping aspect ratio
        self.image_display.setPixmap(pixmap.scaled(400, 300, Qt.AspectRatioMode.KeepAspectRatio))

    def handle_error(self, msg):
        self.label.setText(f"Error: {msg}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PureRefLite()
    window.show()
    sys.exit(app.exec())