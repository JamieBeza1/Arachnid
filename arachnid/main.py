import logging
from arachnid.fetcher import RSSFetcher
from arachnid.parser import Parser
from arachnid.sanitisation import SanitiseArticles
from arachnid.classification import ArticleClassifier
from arachnid.cache import Cache
from arachnid.logger import get_logger

logger = get_logger(__name__,logging.DEBUG)

def process_feed(url, source):
    try:
        logger.info(f"[{source}] Fetching RSS feed")
        xml = RSSFetcher.fetch(url)
        parser = Parser(xml, source)
    except Exception as e:
        logger.error(f"[{source}] Failed to fetch RSS feed: {e}")
        
    
    
    logger.debug(f"[{source}] Beginning article processing")
    for article in parser.parse_xml():
        ok, _ = SanitiseArticles.buzzwords_in_title(article.title)
        if not ok:
            continue
        
        fingerprint = ArticleClassifier.fingerprint(article.title, article.pub_date)
        logger.debug(f"[{source}]Fingerprint generated")

        if Cache.exists(fingerprint, article.title):
            continue
        
        Cache.add_title_to_cache(fingerprint,article.title, article.source)
        logger.info(f"[{source}] New article cahced: {article.title}")
        