from urllib.parse import urlparse
from re import fullmatch


def is_pinterest_link(url: str) -> list:
    """
    Checks if pinterest url is made of 2 parts.
    eturns
    """
    parsed = urlparse(url)

    if parsed.hostname not in {"pinterest.com", "www.pinterest.com"}:
        return []

    parts = [p for p in parsed.path.split("/") if p]

    if len(parts) != 2:
        return []
    return parts


def is_pinterest_board(url: str) -> bool:
    """
    Checks if url is made of user-name/board-name and returns whether true or not.
    Could be buggy, but so far seems accurate to pinterest url structure
    """
    parts = is_pinterest_link(url)
    if not parts:
        return False

    # Exclude known Pinterest non-board routes
    reserved = {
        "pin", "search", "ideas", "today", "login",
        "signup", "settings", "business", "explore",
        "categories", "topics"
    }

    if parts[0].lower() in reserved:
        return False

    return True

def is_pinterest_pin(url: str) -> bool:
    """
    Checks if url is made of pin/pin-name and returns whether true or not.
    Could be buggy
    """
    parts = is_pinterest_link(url)
    if not parts:
        return False

    if parts[0].lower() == "pin":
        return True

    return False


def is_pinterest_image(url: str) -> bool:
    """
    Checks if url is a pinterest image url
    """
    parsed = urlparse(url)

    if parsed.hostname not in {"i.pinimg.com"}:
        return False

    parts = [p for p in parsed.path.split("/") if p]

    if not parts:
        return False

    if fullmatch(r"\d+x", parts[0]) :
        return True

    return False