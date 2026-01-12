import re, logging
from arachnid.models import SoftwareIdentity
from arachnid.logger import get_logger

logger = get_logger(__name__, logging.DEBUG)

class BuzzwordBasedExtractor:
    common_vendors = [
        "microsoft", "google", "apple", "n8n", "veeam", "vmware", "cisco", "oracle", "broadcom", "docker"
        ]
    
    def extract(self, title, body):
        text = f"{title} {body}".lower()
        vendor = next((vendor for vendor in self.common_vendors if vendor in text), "unknown")
        
        product = vendor  # defualt for now until ai integration
        
        match = re.search(r"(?:v?)(\d+\.\d+(?:\.\d+)*)", text)
        version = match.group(1) if match else None
        
        return SoftwareIdentity(
            vendor=vendor,
            product=product,
            version=version or "unknown"
        )