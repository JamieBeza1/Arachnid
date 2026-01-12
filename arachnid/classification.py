import logging, re
from datetime import datetime
from arachnid.logger import get_logger

logger = get_logger(__name__, logging.DEBUG)

class ArticleClassifier:
    # Strings that may commonly indicate a title to be addressing a vulnerability
    vulnerability_indicators = ["vulnerability",
                                "flaw",    
                                "cve",
                                "cvss",
                                "bypass",
                                "rce",
                                "remote code execution",
                                "unauthenticated",
                                "authentication bypass"
                                ]
    # Strings that may commonly indicate a title to be addressing malware
    malware_indicators = ["malware",
                          "worm",
                          "trojan",
                          "stealer",
                          "rat",
                          "backdoor",
                          "spyware",
                          "botnet",
                          "loader",
                          "payload"]
    # software type map used to help identify what software we are dealing with
    software_types = {
        "npm": {
            "indicators": ["npm", "node", "js", "package", "registry", "javascript", "repository"],
            "weight": 1
            },
                        
        "python": {
            "indicators": ["python", "pypi", "pip", "wheel", "egg"],
            "weight": 1
        },
        
        "golang": {
            "indicators": ["golang", "go", "go module", "go package", "go.mod"],
            "weight": 1
        },
        
        "nuget": {
            "indicators": ["nuget", "dotnet", ".net", "c#"],
            "weight": 1
        },
        
        "maven": {
            "indicators": ["maven", "java", "pom.xml", "mvn", "mvnrepository"],
            "weight": 1
        },
        
        "docker": {
            "indicators": ["docker", "image", "dockerfile", "container"],
            "weight": 1
        },
        
        "browser-extension": {
            "indicators": ["browser", "chrome", "extension", "addon", "firefox", "edge"],
            "weight": 1
        },
        
        "unknown": {
            "indicators": [""],
            "weight": 1
        },
    }
    
    @classmethod
    def threat_type(cls, title):
        title = title.lower()
        logger.debug(f"Determining threat type for title: {title}")
        
        # checks if title contains any vulnerability indicators
        if any(word in title for word in cls.vulnerability_indicators):
            logger.info(f"Threat claasified as VULNERABILITY for title: {title}")
            return "V"
        
        # checks if title contains any malware indicators
        if any(word in title for word in cls.malware_indicators):
            logger.info(f"Threat classified as MALWARE for title: {title}")
            return "M"
        
        logger.info(f"Threat classified as UNKNOWN for title: {title}")
        return "U"
    
    @staticmethod
    def date_stamp(pubdate):
        # method to translate the pubdate recevied from the article xml to a suitable format
        # format translation: Wed, 07 Jan 2026 13:05:42 -0500 -> 07012026
        dt = datetime.strptime(pubdate,"%a, %d %b %Y %H:%M:%S %z")
        formatted_date = dt.strftime("%d%m%Y")
        logger.debug(f"Formatted date: {pubdate} -> {formatted_date}")
        return formatted_date
    
    @classmethod
    def software_type(cls, title):
        title = title.lower()
        logger.info(f"Determinig software type from: {title}")
        for name, data in cls.software_types.items():
            # if title contains any of the software type buzzwords, then it gets categorised as that type
            if any(word in title for word in data["indicators"]):
                logger.info(f"Software Identified as '{name}' for title: {title}")
                return name
        logger.info(f"Software identified as 'unknown' for title: {title}")
        return "unknown"
    
    @staticmethod
    def extract_version(title):
        match = re.search(r"\b(v?\d+(\.\d+){1,3})\b", title.lower())
        return match.group(1) if match else "unknown"
    
    @staticmethod
    def extract_vendor(title):
        known_vendors = [
        "microsoft", "google", "apple", "veeam", "cisco", "fortinet",
        "vmware", "docker", "npm", "python", "oracle", "n8n", "broadcom"
        ]
        
        for vendor in known_vendors:
            if vendor in title.lower():
                return vendor
        return "unknown"
        
    
    @classmethod
    def fingerprint(cls, title):
        # creates fingerprint to save data under: FORMAT = <threat_type>:<software_type>:<date>
        vendor = cls.extract_vendor(title)
        product = vendor
        version = cls.extract_version(title)
        
        fingerprint = f"{vendor}:{product}:{version}"
        logger.info(f"Fingerprint generated for title: {title} ({fingerprint})")
        return fingerprint