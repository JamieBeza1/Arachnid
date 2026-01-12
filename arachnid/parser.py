import logging
import xml.etree.ElementTree as ET
from arachnid.models import Article
from arachnid.logger import get_logger
from arachnid.fetcher import HTMLFetcher

logger = get_logger(__name__, logging.DEBUG)

class Parser:
    # parser class to handle all xml parsing and article object creation
    def __init__(self, xml_bytes, source):
        self.xml = xml_bytes
        self.source = source
        
    def parse_xml(self):
        try:
            # gets root of xml    
            root = ET.fromstring(self.xml)
            logger.debug(f"XML Successfully parsed:")
        except ET.ParseError as e:
            logger.error(f"Failed to parse XML for source: {self.source}")

        channel = root.find("channel")
        if channel is None:
            logger.warning(f"No <channel> found in RSS feed's XML for source: {self.source}")
            raise
        # RSS feeds store articles under <item> XML tags
        items = channel.findall("item")
        logger.info(f"Found {len(items)} items in RSS feed from: {self.source}")

        # iterates over each found article
        for item in items:
            title = item.findtext("title")
            link = item.findtext("link")
            #description = item.findtext("description")
            pub_date=item.findtext("pubDate")
            source=self.source
            
            if not title or not link:
                logger.warning(f"skipping item with missing data: {self.source}")
                continue
            
            # Obtains description from url
            description = HTMLFetcher.get_html(link)
            logger.debug(description)
            
            # Creates article object to store data in    
            article = Article(
                title=title,
                link=link,
                description=description,
                pub_date=pub_date,
                source=source
            )
            logger.debug(f"Creating Article Object: {title}")
            yield article
