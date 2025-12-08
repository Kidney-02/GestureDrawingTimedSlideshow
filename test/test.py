import sys
import os
import requests # Required for network requests
from bs4 import BeautifulSoup
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QDragMoveEvent
from PySide6.QtWidgets import QWidget, QApplication, QLabel, QVBoxLayout

class DropTargetWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.label = QLabel("Drag a URL here to check and download the image.")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout = QVBoxLayout(self)
        layout.addWidget(self.label)
        self.setWindowTitle("URL Image Downloader")
        self.setMinimumSize(400, 200)

    # --------------------------------------------------------------------
    # 1. Drag Event Handlers (No change from before)
    # --------------------------------------------------------------------

    def dragEnterEvent(self, event: QDragEnterEvent):
        """Accepts the drag if the MIME data contains URLs."""
        if event.mimeData().hasUrls():
            event.acceptProposedAction() 
        else:
            event.ignore()

    def dragMoveEvent(self, event: QDragMoveEvent):
        """Controls the cursor feedback."""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    # --------------------------------------------------------------------
    # 2. Drop Event Handler (The main logic)
    # --------------------------------------------------------------------

    def dropEvent(self, event: QDropEvent):
        # ... (Same logic as before to extract web_urls) ...
        mime_data = event.mimeData()
        if mime_data.hasUrls():
            urls = mime_data.urls()
            web_urls = [url for url in urls if url.scheme().lower().startswith(('http', 'https'))]
            
            if web_urls:
                url_str = web_urls[0].toString()
                self.label.setText(f"Processing URL: {url_str}...")
                
                try:
                    self.process_url(url_str)
                    event.acceptProposedAction()
                except Exception as e:
                    self.label.setText(f"Error: {e}")
                    event.ignore()
            else:
                self.label.setText("Dropped item is a local file, not a web URL (http/https).")
                event.ignore()
        else:
            event.ignore()

    # --------------------------------------------------------------------
    # 3. Network and File Saving Logic
    # --------------------------------------------------------------------

    def download_image_file(self, image_url: str, directory="downloaded_images"):
        """Downloads a single image file from a direct URL."""
        if not os.path.exists(directory):
            os.makedirs(directory)
            
        # 1. Use requests.head to get the file extension/type
        head_response = requests.head(image_url, timeout=5)
        head_response.raise_for_status()
        
        content_type = head_response.headers.get('Content-Type', '').lower()
        if not 'image/' in content_type:
            # Skip if the link found isn't an image URL
            return None 

        # 2. Get the file name
        ext = content_type.split('/')[-1] if '/' in content_type else 'jpg'
        # Create a basic file name using the URL's hash or a simple counter
        file_name = f"{hash(image_url)}.{ext}"
        full_path = os.path.join(directory, file_name)

        # 3. Download the actual image data
        image_response = requests.get(image_url, stream=True, timeout=30)
        image_response.raise_for_status()
        
        with open(full_path, 'wb') as f:
            for chunk in image_response.iter_content(chunk_size=8192):
                f.write(chunk)
                
        return full_path

    def process_url(self, url: str):
        """
        Processes the dropped URL. It first checks if the URL is a direct image 
        and downloads it. If not, it attempts to scrape images from the HTML content.
        """
        download_count = 0
        
        # 1. First, check if the URL is a direct image file (from the previous method)
        try:
            downloaded_path = self.download_image_file(url)
            if downloaded_path:
                self.label.setText(f"✅ Downloaded direct image:\n{downloaded_path}")
                return
        except requests.exceptions.HTTPError:
            # If it fails, assume it's a webpage, not a direct image file
            pass 
        
        # 2. If it's not a direct image, assume it's a webpage and scrape it
        self.label.setText("URL is a webpage. Attempting to scrape images...")
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        # Check if the content is HTML
        content_type = response.headers.get('Content-Type', '').lower()
        if 'text/html' not in content_type:
            self.label.setText(f"Content is not HTML (Type: {content_type}). Cannot scrape.")
            return

        # Use Beautiful Soup to parse the HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all <img> tags
        img_tags = soup.find_all('img')
        
        # Limit the number of downloads to prevent abuse or long waits
        MAX_DOWNLOADS = 5
        
        for img in img_tags:
            src = img.get('src')
            if src and download_count < MAX_DOWNLOADS:
                # Construct the absolute URL if the src is relative
                full_image_url = QUrl(url).resolved(QUrl(src)).toString()
                
                try:
                    self.download_image_file(full_image_url)
                    download_count += 1
                except Exception as e:
                    # Silently skip bad/broken image links
                    print(f"Skipping bad image URL {full_image_url}: {e}") 
                    
        # Final status update
        if download_count > 0:
            self.label.setText(f"✅ Success! Found and downloaded {download_count} image(s) to 'downloaded_images' folder.")
        else:
            self.label.setText("🚫 No images found on the linked webpage.")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = DropTargetWidget()
    window.show()
    sys.exit(app.exec())