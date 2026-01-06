from arachnid.fetcher import RSSFetcher
from arachnid.parser import Parser
from arachnid.sanitisation import SanitiseArticles
from arachnid.classification import ArticleClassifier
from arachnid.cache import Cache

def process_feed(url, source):
    xml = RSSFetcher.fetch(url)
    
    parser = Parser(xml, source)
    
    for article in parser.parse_xml():
        ok, _ = SanitiseArticles.buzzwords_in_title(article.title)
        if not ok:
            continue
        
        fingerprint = ArticleClassifier.fingerprint(article.title, article.pub_date)
        
        if Cache.exists(fingerprint, article.title):
            continue
        
        Cache.add_title_to_cache(fingerprint,article.title, article.source)
        

"""
def run(site):
    print(f"...Fetching: {site.__class__.__name__}")
    try:
        site.fetch_and_parse_xml()  # 1st method being called to fetch
        print(f"Articles Found: {len(site.extracted_data)}")
        for article in site.extracted_data:
            print(f"-> {article['title']}")
    except Exception as e:
        print(f"Error processing site - {site.__class__.__name__.upper()}: {e}")
        
def main():
    sites = [HackerNews(),
             BleepingComputer()]
    
    for site in sites:
        run(site)
"""    
#main()