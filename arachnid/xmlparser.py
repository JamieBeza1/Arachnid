import requests, cloudscraper, re
import xml.etree.ElementTree as ET
from datetime import datetime

from sanitisation import SanitiseArticles
        

class RSSParser:
    """ Class to handle all website RSS feeds to obtain data and to manipulate found vulnerabilities/malicious packages"""
    def __init__(self, url):
        self.url = url
        self.xml = self._get_xml()
        #print(self.xml)
        self.extracted_data = []
        
    def _looks_like_xml(self, response):
        # checks headers to determine if the pge contains xml or antibot checks
        content_type = response.headers.get("Content-Type","").lower()
        
        if "xml" in content_type:
            return True
        
        text = response.text.lower()
        if text.lstrip().startswith("<?xml"):   # Checks leftmost strings start with the xml tags
            return True        
        else:
            return False    # assumes an antibot page is present
        
        
    def _get_xml(self):
        """This method attempts to get the xml from the rss url, checks if it looks like xml, 
        otherwise attempting to bypass antibot mechanisms"""
        #xml = requests.get(self.url, timeout=10)
        try:
            response = requests.get(self.url, timeout=10)
            response.raise_for_status()
            
            if self._looks_like_xml(response):
                return response.content
            else:
                print("Normal request returned non-XML, trying cloudscraper...")
        except requests.RequestException as e:
            print(f"Normal Request Failed: {e}")
            
        try:
            # scraper module used to bypass antibot by simulating browser
            print("Attempting to bypass Anti-Bot...")
            scraper = cloudscraper.create_scraper()
            response = scraper.get(self.url, timeout=10)
            response.raise_for_status()
            
            if self._looks_like_xml(response):
                return response.content
            else:
                raise RuntimeError("Cloudscraper returned non-XML content")
        
        except Exception as e:
            raise RuntimeError(f"Failed to obtain RSS XML: {e}")
            
    def handle_xml(self):
        #print(self.xml)
        root = ET.fromstring(self.xml)
        channel = root.find("channel")

        #extracts all necessary data from rss feed XML 
        for item in channel.findall("item"):
            self.extracted_data.append({
                "title": item.findtext("title"),
                "link": item.findtext("link"),
                "description": item.findtext("description"),
                "pub_date": item.findtext("pubDate")
                })
        """    
        for i in range(len(self.extracted_data)):
            title = self.extracted_data[i]["title"]
            print(f"TITLE: {title}")
        """
        for item in self.extracted_data:
            title = item["title"]
            success, buzzword = SanitiseArticles.buzzwords_in_title(title)
            if success:
                #print(f"BUZZWORD MATCHED ~~ {buzzword} ~~  :  {title}")
                RSSDataCacher.create_id_string(title, item["pub_date"])
                #v, p = RSSDataCacher.infer_vendor_product_values(title)
                #print(f"VENDOR:   {v} ::::: PRODUCT:   {p}")
                data = FingerprintBuilder.build_fingerprint(title, item["pub_date"])
                print(data)
                
                
            #else:
                #print(f"REDUNDANT ARTICLE: {item["title"]}")            
        
        
class RSSDataCacher:
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
    
    context_keywords = {
        "product": ["flaw", "vulnerability", "bug", "research", "exploits"],
        "vendor": ["warns", "issues", "flags", "found", "by", "identified"]
    }
    
    ecosystems = {
        "npm": ["npm", "node", "node.js", "javascript", "js"],
        "pypi": ["pypi", "pip", "python", "wheel"],
        "maven": ["maven", "java", "jar"],
        "nuget": ["nuget", ".net", "dotnet", "c#"],
        "docker": ["docker", "container", "image"],
        "browser-ext": ["chrome", "firefox", "extension", "addon", "edge"],
    }
    
   
    @classmethod
    def classify_threat(self, title):
        for ind in self.vulnerability_indicators:
            if ind in title.lower():
                return "V"
        for ind in self.malware_indicators:
            if ind in title.lower():
                return "M"
        return "U"  # for unknowns
    
    @classmethod
    def set_date(self, pubdate):
        dt = datetime.strptime(pubdate, "%a, %d %b %Y %H:%M:%S %z")
        formatted = dt.strftime("%d%m%Y")
        return formatted
    
    @classmethod
    def infer_software_type(self, title):
        scores = {}
        for type, data in self.software_types.items():
            for indicator in data["indicators"]:
                if indicator in title.lower():
                    # appends to existing score values
                    scores[type] = scores.get(type, 0) + data["weight"]
                    
        if not scores:
            return "unknown"
        
        return max(scores, key=scores.get)
                
    @classmethod        
    def create_id_string(self, title, pubdate):
        delimeter = ":"
        threat_type = self.classify_threat(title)
        date = self.set_date(pubdate)
        software_type = self.infer_software_type(title)
        
        #creates string from other methods
        id_string = f"{threat_type}:{date}:{software_type}"
        print(f"HEADLINE:   {title}  :  ID string generated:   {id_string}")
    
    # tokenises word in title
    @classmethod   
    def tokeniser(self, title):
        return re.findall(r"[A-Za-z][A-Za-z0-9\-]+", title)
    
    # extracts words starting with upper cased chars
    @classmethod
    def extract_nouns(self, title):
        return re.findall(r"(?:[A-Z][a-zA-Z0-9\-]+(?:\s+[A-Z][a-zA-Z0-9\-]+)*)", title)
    
    @classmethod
    def score_candidates(self, title, span):
        score = 0
        title = title.lower()
        span = span.lower()
        
        #proximety scoring of keywords from product buzzwords
        for keyword in self.context_keywords["product"]:
            if keyword in title and abs(title.index(keyword) - title.index(span)) <40:
                score += 3
        # proximety scorign of keywords from vendor buzzwords
        for keyword in self.context_keywords["vendor"]:
            if keyword in title and title.index(span) < title.index(keyword):
                score += 2
                
        if len(span.split()) > 1:
            score += 2
        
        return score
    
    @classmethod
    def infer_vendor_product_values(self, title):
        spans = self.extract_nouns(title)
        if not spans:
            return "unknown", "unknown"
        
        scored = [(span, self.score_candidates(title, span)) for span in spans]
        scored.sort(key=lambda x: x[1], reverse=True)
        
        product = scored[0][0]
        
        vendor = "unknown"
        for span, _ in scored[1:]:
            if len(span.split()) <= 2:
                vendor = span
                break
        return vendor.lower(), product.lower()
        

class FingerprintBuilder:
    vulnerabiltiy_indicators = [
        "vulnerability", "flaw", "cve", "cvss",
        "bypass", "rce", "remote code execution",
        "unauthenticated"
    ]

    malware_indicators = [
        "malware", "worm", "trojan", "stealer",
        "rat", "botnet", "backdoor", "loader"
    ]
    
    ecosystems = {
        "npm": ["npm", "node", "node.js", "javascript", "js"],
        "pypi": ["pypi", "pip", "python", "wheel"],
        "maven": ["maven", "java", "jar"],
        "nuget": ["nuget", ".net", "dotnet", "c#"],
        "docker": ["docker", "container", "image"],
        "browser-ext": ["chrome", "firefox", "extension", "addon", "edge"],
    }
    
    stopwords = {
        "critical", "flaw", "malware", "vulnerability",
        "attack", "exploits", "allows", "active",
        "found", "using", "used", "allows"
    }
    """General pipeline consists of:
    1) tokenising titles into words
    2) sanitising tokens & stripping padded unnecessary words
    3) alphabetically sorting tokens
    4) creating id string of threat-type, ecosystem, date to store under
    5) performing fuzzy lookup of similar keywords currently pre-existing in the json
    """
    
    #tokenisation of titles into string arrays:
    @staticmethod
    def tokenise_string(title):
        return re.findall(r"[A-Za-z][A-Za-z0-9\-]+", title)
    
    @staticmethod
    def identify_nouns(title):
            
    
    @staticmethod
    def normalise(text):
        text = text.lower()
        text = re.sub(r"[^a-z0-9\s\-]", " ", text) 
        text = re.sub(r"\s+", " ", text)
        return text.strip()   
    
    @classmethod
    def classify_threat(cls, title):
        title = cls.normalise(title)
        for k in cls.vulnerabiltiy_indicators:
            if k in title:
                return "V"
        for k in cls.malware_indicators:
            if k in title:
                return "M"
        return "U"
    
    
    @classmethod
    def detect_ecosystem(cls, title):
        title = cls.normalise(title)
        for eco, words in cls.ecosystems.items():
            for w in words:
                if w in title:
                    return eco
        return "unknown"
    
    
    @classmethod
    def extract_product_tokens(cls, title):
        title = cls.normalise(title)
        tokens = re.findall(r"[a-z][a-z0-9\-]{3,}", title)
        return sorted(set(t for t in tokens if t not in cls.stopwords))
    
    @staticmethod
    def time_bucket(pubdate):
        dt = datetime.strptime(pubdate, "%a, %d %b %Y %H:%M:%S %z")
        return dt.strftime("%Y-%W")  # year-week

    
    @classmethod
    def build_fingerprint(cls, title, pubdate):
        threat = cls.classify_threat(title)
        ecosystem = cls.detect_ecosystem(title)
        tokens = cls.extract_product_tokens(title)
        bucket = cls.time_bucket(pubdate)

        payload = {
            "t": threat,
            "e": ecosystem,
            "k": tokens,
            "b": bucket
        }

        #raw = json.dumps(payload, sort_keys=True)
        #return hashlib.sha256(raw.encode()).hexdigest()[:16]
        threat_string = f"THREAT: {threat} | ECOSYSTEM: {ecosystem} | TOKENS: {tokens} | BUCKET: {bucket}"
        return threat_string
    
    
if __name__=="__main__":
    parse = RSSParser("https://www.bleepingcomputer.com/feed/")
    parse.handle_xml()