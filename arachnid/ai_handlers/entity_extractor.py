import logging
from arachnid.logger import get_logger
from arachnid.models import TitleExtraction, ArticleExtraction

logger = get_logger(__name__, logging.DEBUG)


class AIExtractor:
    """
    This class will eventually be used to call GCP's Vertex AI.
    For now, it returns mock data
    """
    
    def extract_from_title(self, title):
        logger.debug("Mock AI extarction of vendor/product from title")
        if not title:
            return TitleExtraction()
        
        if "n8n" in title.lower():
            return TitleExtraction(
                vendor="n8n",
                product="n8n",
                confidence=0.92
            )
            
        return TitleExtraction()
        
    # full article extraction - AI EXPENSIVE
    def extract_from_article(self, title, body):
        logger.debug("Mock AI extraction of full article details")
        
        if not title and not body:
            return ArticleExtraction()
        
        combined = f"{title} {body}".lower()
        
        if "n8n" in combined:
            vendor = "n8n"
            product = "n8n"
            version = "unknown"
            cves = ["CVE-2026-XXXX"]
            summary = "Mocked n8n summary for testing"
        
            keywords = self.build_keywords(
                vendor=vendor,
                product=product,
                version=version,
                cves=cves,
            )
            
            return ArticleExtraction(
                vendor=vendor,
                product=product,
                version=version,
                cves=cves,
                summary=summary,
                keywords=keywords
            )
        return ArticleExtraction(
            keywords=self.build_keywords(
                vendor="UNKNOWN_VENDOR",
                product="UNKNOWN_PRODUCT",
                version="UNKNOWN_VERSION",
                cves=[]
            )
        )
    
    def build_keywords(self, vendor, product, version, cves):
        keywords = []
        vendor = vendor.lower()
        product = product.lower()
        version = version.lower()
        
        if vendor:
            keywords.append(f"{vendor}")
        if vendor and product:
            keywords.append(f"{vendor}:{product}")
        if vendor and product and version != "unknown":
            keywords.append(f"{vendor}:{product}:{version}")
            
        for cve in cves:
            keywords.append(f"cve:{cve}")
        
        logger.debug(f"Generated keywords: {keywords}")
        return keywords