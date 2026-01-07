import requests, logging
from arachnid.logger import get_logger

logger = get_logger(__name__, logging.DEBUG)


class RSSFetcher:
    # sets user agent to bypass Cloudflare antibot mechs
    defualt_headers = {
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "application/rss+xml,application/xml;q=0.9,*/*;q=0.8"
    }
    
    @staticmethod
    def looks_like_xml(response):
        content_type = response.headers.get("Content-Type", "").lower()
        # Checks if the content appears to be xml, as antibot pages are NOT
        if "xml" in content_type:
            return True
        return response.text.lstrip().startswith("<?xml")

    @classmethod
    def fetch(cls, url, timeout=10):
        logger.info(f"Fetching RSS feed from URL: {url}")
        try:
            response = requests.get(url, headers=cls.defualt_headers, timeout=timeout)
            
            #checks http status code is successful ie in range 200-299, otherwise raising error
            response.raise_for_status()
            
            logger.info(f"Successfully fetched feed: {url}")
            
        except requests.RequestException as e:
            logger.error(f"Failed to fetch RSS feed from {url}: {e}")
            raise

        if not cls.looks_like_xml(response):
            logger.warning(f"Fetched content doesnt appear to be XML: {url}")
            raise ValueError("Non-XML Response")
        
        logger.info(f"XML feed validated for URL: {url}")
        return response.content
        