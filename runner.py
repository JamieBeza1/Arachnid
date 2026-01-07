import logging
from arachnid.main import process_feed
from arachnid.logger import get_logger
from arachnid.utils import print_ascii_art

# feeds to search through
feeds = [
    ("https://feeds.feedburner.com/TheHackersNews", "TheHackerNews"),
    ("https://www.bleepingcomputer.com/feed/", "BleepingComputer"),
]

logger = get_logger(__name__,logging.DEBUG)

def main():
    for url, name in feeds:
        try:
            logger.info(f"Processing feed {name}")
            process_feed(url, name)
        except Exception as e:
            logger.critical(f"Fatal error processing {name}: {e}")
            raise
            
            
if __name__=="__main__":
    print_ascii_art()
    main()
    
    
    
"""
EXAMPLE ARTICLES THAT ARE THE SAME BUT DELAYED IN REPORTING:
https://www.bleepingcomputer.com/news/security/clickfix-attack-uses-fake-windows-bsod-screens-to-push-malware/
https://thehackernews.com/2026/01/fake-booking-emails-redirect-hotel.html
"""