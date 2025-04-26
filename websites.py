from crawler import Crawler

class Hackernews(Crawler):
    def __init__(self):
        super().__init__("https://feeds.feedburner.com/TheHackersNews")

    def crawl(self):
        super().crawl()
        
        
   
class Bleepingcomputer(Crawler):
    def __init__(self):
        super().__init__("https://www.bleepingcomputer.com/feed/")

    def crawl(self):
        super().crawl()
