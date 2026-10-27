import os
import re
import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import hashlib


def download_pinterest_board(board_url :str, output_dir :str):
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
    filepaths = []

    for element in elements:

        urls = set(re.findall(
            r'https?://i\.pinimg\.com/[^"\'\s<>]+',
            str(element)
        ))

        for url in sorted(urls):
            url = re.sub(r'\d+x/', '1200x/', url, count=1)
            print("Image URL:", url)
            filepath = download_image(url, output_dir)
            if filepath is not None:
                filepaths.append(filepath)

    pass
    return filepaths



def download_image(url :str, output_dir :str):

    os.makedirs(output_dir, exist_ok=True)

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/130.0.0.0 Safari/537.36"
        )
    }

    try:
        response = requests.get(
            url, headers=headers, timeout=20
        )
        response.raise_for_status()

        content_type = response.headers.get("Content-Type", "").lower()

        # If this URL returns an image directly, save it.
        if content_type.startswith("image/"):
            data = response.content
            image_url = response.url

        # Otherwise, treat it as a webpage and extract an image URL.
        elif "text/html" in content_type:
            soup = BeautifulSoup(response.text, "html.parser")

            image_url = None

            # Prefer Pinterest's main image metadata.
            for selector, attr in [
                ('meta[property="og:image"]', "content"),
                ('meta[name="twitter:image"]', "content"),
            ]:
                tag = soup.select_one(selector)
                if tag and tag.get(attr):
                    image_url = tag[attr]
                    break

            if not image_url:
                raise ValueError("No image URL found on the page")

            # Download the extracted image.
            return download_image(image_url, output_dir)

        else:
            raise ValueError(f"URL did not return an image or HTML: {content_type}")

        # Determine an extension and generate a safe filename.
        extension = os.path.splitext(urlparse(image_url).path)[1].lower()
        if extension not in {".jpg", ".jpeg", ".png", ".webp", ".gif"}:
            extension = ".jpg"

        # filename = re.sub(
        #     r"[^a-zA-Z0-9_.-]", "_",
        #     os.path.basename(urlparse(image_url).path)
        # ) or f"image{extension}"
        #
        # if filename == 'image':
        #     filename = str(hash(image_url))
        #
        # if not os.path.splitext(filename)[1]:
        #     filename += extension

        filename = hashlib.sha256(data).hexdigest() + extension

        filepath = os.path.join(output_dir, filename)

        if os.path.exists(filepath):
            print(f"Image already downloaded: {filepath}")
            return filepath


        with open(filepath, "wb") as f:
            f.write(data)

        print(f"Downloaded: {filepath}")
        return filepath

    except (requests.RequestException, ValueError) as e:
        print(f"Download failed: {e}")
        return None





    #### Testing

    # Pinterest pin page


# dl_image_from_url(
#     "https://www.pinterest.com/pin/520728775689254479/",
#     r"C:\Users\juoza\Downloads\Test"
# )
#
# # Direct Pinterest image
# dl_image_from_url(
#     "https://i.pinimg.com/1200x/58/f1/92/58f192fc0f72cad22b2f1b906e8046f9.jpg",
#     r"C:\Users\juoza\Downloads\Test"
# )
#
# # Google thumbnail
# dl_image_from_url(
#     "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSBTRn82zhNiSz4MH6ZFUyRdh6KdZRfR1DtkSMm0p7uvQ&s=10",
#     r"C:\Users\juoza\Downloads\Test"
# )