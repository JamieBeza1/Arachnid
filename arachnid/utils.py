import os, logging, time
from arachnid.logger import get_logger

logger = get_logger(__name__, logging.DEBUG)

# spider descend ascii animation
def spider_descend(delay=0.15, steps=10):
    art_file = os.path.join(os.path.dirname(__file__), "resources","arachnid_art.txt")

    with open(art_file, "r") as f:
        art_lines = f.readlines()
    for step in range(steps):
        os.system("cls" if os.name == "nt" else "clear")
        
        for _ in range(step):
            # sting for webbing
            print("     |                        |                     |")

        for line in art_lines:
            print(line.rstrip())

        time.sleep(delay)
    print_arachnid_title()
    time.sleep(3)

# prints tool name art and banner
def print_arachnid_title():
    art_file = os.path.join(os.path.dirname(__file__), "resources","arachnid_text_art.txt")

    with open(art_file, "r") as f:
        art_lines = f.readlines()
    for line in art_lines:
        print(line, end="")
