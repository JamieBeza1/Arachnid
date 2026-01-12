import logging
from arachnid.fetcher import RSSFetcher, HTMLFetcher
from arachnid.parser import Parser
from arachnid.sanitisation import SanitiseArticles
from arachnid.classification import ArticleClassifier
from arachnid.cache import Cache
from arachnid.logger import get_logger
from arachnid.ai_handlers.entity_extractor import AIExtractor

logger = get_logger(__name__,logging.DEBUG)
ai = AIExtractor()

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
        return
            
    logger.debug(f"[{source}] Beginning article processing")
    
    for article in parser.parse_xml():
        # 1) CHEAP LOCAL CHECKS
        # checks if the article title has any favoured buzzwords
        ok, _ = SanitiseArticles.buzzwords_in_title(article.title)
        if not ok:
            continue
        
        # 2) AI TITLE EXTRACTION (CHEAP & MINIMAL)
        title_ai = ai.extract_from_title(article.title)
        
        # checks confidence score
        if not title_ai.vendor or title_ai.confidence < 0.7:
            logger.debug(f"[{source}] AI confidence score is too low, skipping...")
            continue
        
        # 3) cheap dedupe before HTML fetching
        # creates fingerprint from article data: Fingerprint derives the cache location
        fingerprint_stub = Cache.build_fingerprint(
            title_ai.vendor,
            title_ai.product,
            "unknown"
        )
        
        if Cache.exists(fingerprint_stub, article.title):
            logger.info("Duplicate Detected (pre-HTML-fetch)")
            continue
        
        # 4) HTML fetch if the title is new
        try:
            body = HTMLFetcher.get_html(article.link)
        except Exception as e:
            logger.warning(f"[{source}] Failed to fetch HTML: {e}")
            continue
        
        # 5) AI FULL EXTRACTION (expensive and full)
        article_ai = ai.extract_from_article(article.title, body)
        
        fingerprint = Cache.build_fingerprint(
            article_ai.vendor or title_ai.vendor,
            article_ai.product or title_ai.product,
            article_ai.version or "unknown"
        )
        
        if Cache.exists(fingerprint, article.title):
            logger.info(f"[{source}] Duplicate Detected(post-ai)")
            continue
                    
        Cache.add_title_to_cache(
            fingerprint=fingerprint,
            title=article.title,
            source=article.source,
            link=article.link,
            description=article.description,
            pub_date=article.pub_date
        ) 
        
        logger.info(f"[{source}] New article cahced: {article.title}")
        
