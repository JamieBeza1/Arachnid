import logging
from arachnid.main import process_feed
from logger import get_logger

feeds = [
    ("https://feeds.feedburner.com/TheHackersNews", "TheHackerNews"),
    ("https://www.bleepingcomputer.com/feed/", "BleepingComputer"),
]

def main():
    for url, name in feeds:
        #try:
        process_feed(url, name)
        #except Exception as e:
        #    print(f"[ERROR] {name}: {e}")
            
            
if __name__=="__main__":
    main()
    
    
    
"""
EXAMPLE ARTICLES THAT ARE THE SAME BUT DELAYED IN REPORTING:
https://www.bleepingcomputer.com/news/security/clickfix-attack-uses-fake-windows-bsod-screens-to-push-malware/
https://thehackernews.com/2026/01/fake-booking-emails-redirect-hotel.html
"""