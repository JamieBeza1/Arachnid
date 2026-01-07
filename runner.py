import logging
from arachnid.main import process_feed
from arachnid.logger import get_logger
from arachnid.utils import spider_descend

# feeds to search through
feeds = [
    ("https://feeds.feedburner.com/TheHackersNews", "TheHackerNews"),
    ("https://www.bleepingcomputer.com/feed/", "BleepingComputer"),
]

logger = get_logger(__name__,logging.DEBUG)

# main entry point to run full scripts from
def main():
    # iterates each url in feed
    for url, name in feeds:
        try:
            logger.info(f"Processing feed {name}")
            process_feed(url, name)
        except Exception as e:
            logger.critical(f"Fatal error processing {name}: {e}")
            raise
            
            
if __name__=="__main__":
    spider_descend()
    main()
    
    
    
"""
EXAMPLE ARTICLES THAT ARE THE SAME BUT DELAYED IN REPORTING:
https://www.bleepingcomputer.com/news/security/clickfix-attack-uses-fake-windows-bsod-screens-to-push-malware/
https://thehackernews.com/2026/01/fake-booking-emails-redirect-hotel.html
"""