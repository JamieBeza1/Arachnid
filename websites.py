from crawler import Crawler

class Hackernews(Crawler):
    def __init__(self, element_classname="home-title"):
        super().__init__("https://thehackernews.com/")
        self.element_classname = element_classname
    
    def crawl_and_extract_h2s(self, element_class_name="home-title"):
        super().crawl_and_extract_h2s(self.element_classname)
    
class Bleepingcomputer(Crawler):
    def __init__(self):
        super().__init__("https://www.bleepingcomputer.com/")

    def crawl_and_extract_h2s(self, element_class_name="title"):
        super().crawl_and_extract_h2s(element_class_name)

    