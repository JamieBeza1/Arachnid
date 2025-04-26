#Main entry point for webcrawler app
from websites import Hackernews, Bleepingcomputer

def hackernews_articles():
    hackernews = Hackernews()
    hackernews.crawl()
    hackernews.write_report()

def bleepingcomputer_articles():
    beepingcomputer = Bleepingcomputer()
    beepingcomputer.crawl()
    beepingcomputer.write_report() 

def main():
    hackernews_articles()
        
if __name__ == "__main__":
    main()