import re
import requests
from bs4 import BeautifulSoup

from UrlParser import *

board_url = "https://www.pinterest.com/tgawhk/test/"

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/130.0.0.0 Safari/537.36"
    )
}

response = requests.get(board_url, headers=headers, timeout=30)

# print("HTTP status:", response.status_code)
# print("Final URL:", response.url)
response.raise_for_status()
html = response.text

# Parse elements whose IDs begin with the requested prefix.
soup = BeautifulSoup(html, "html.parser")
elements = soup.find_all(
    id=lambda value: value and value.startswith("board-image-preload-")
)
for element in elements:

    urls = set(re.findall(
        r'https?://i\.pinimg\.com/[^"\'\s<>]+',
        str(element)
    ))

    for url in sorted(urls):
        url = re.sub(r'\d+x/', '1200x/', url, count=1)
        print("Image URL:", url)