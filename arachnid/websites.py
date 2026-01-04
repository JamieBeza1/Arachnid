from arachnid.xmlparser import RSSParser

class Website:
    def __init__(self, url: str):
        self.url = url
        self.rss_parser = RSSParser(url)
        self.extracted_data = []
    
    def fetch_and_parse_xml(self):
        """fetches XML and processes data"""
        self.rss_parser.handle_xml()
        self.extracted_data = self.rss_parser.extracted_data
        
        
class HackerNews(Website):
    def __init__(self):
        super().__init__("https://feeds.feedburner.com/TheHackersNews")

class BleepingComputer(Website):
    def __init__(self):
        super().__init__("https://www.bleepingcomputer.com/feed/")
