#Main entry point for webcrawler app
from websites import Hackernews

def hackernews_articles(html_class_name):
    hackernews = Hackernews(element_classname=html_class_name)
    hackernews.crawl_and_extract_h2s()
    hackernews.write_report()

    

def main():
    hackernews_articles("home-title")
        
if __name__ == "__main__":
    main()