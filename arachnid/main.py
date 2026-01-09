import logging
from arachnid.fetcher import RSSFetcher
from arachnid.parser import Parser
from arachnid.sanitisation import SanitiseArticles
from arachnid.classification import ArticleClassifier
from arachnid.cache import Cache
from arachnid.logger import get_logger

logger = get_logger(__name__,logging.DEBUG)

# function to get xml from supplied url
def process_feed(url, source):
    try:
        logger.info(f"[{source}] Fetching RSS feed")
        # Attempts to get RSS feed
        xml = RSSFetcher.fetch(url)
        # parses xml and creates object 
        parser = Parser(xml, source)
    except Exception as e:
        logger.error(f"[{source}] Failed to fetch RSS feed: {e}")
        
    logger.debug(f"[{source}] Beginning article processing")
    
    for article in parser.parse_xml():
        # checks if the article title has any favoured buzzwords
        ok, _ = SanitiseArticles.buzzwords_in_title(article.title)
        if not ok:
            continue
        
        # creates fingerprint from article data: Fingerprint derives the cache location
        fingerprint = ArticleClassifier.fingerprint(article.title, article.pub_date)
        logger.debug(f"[{source}]Fingerprint generated")

        # checks if the cache exists for the title & fingerprint
        if Cache.exists(fingerprint, article.title):
            continue
        
        # Calls caching function to add to /cache directory
        Cache.add_title_to_cache(fingerprint,article.title, article.source, article.link, article.description, article.pub_date)
        logger.info(f"[{source}] New article cahced: {article.title}")
        