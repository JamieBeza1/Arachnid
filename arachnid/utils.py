import os, logging, time
from arachnid.logger import get_logger

logger = get_logger(__name__, logging.DEBUG)

def print_ascii_art():
    art_path = os.path.join(os.path.dirname(__file__), "resources","arachnid_art.txt")
    try:
        with open(art_path, "r") as f:
            art = f.read()
        print(art)
        time.sleep(1)
    except FileNotFoundError:
        logger.warning("ASCII art file not found!")