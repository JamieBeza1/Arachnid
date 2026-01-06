import requests, cloudscraper, re, os, json
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from fuzzywuzzy import fuzz

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
        
        # set a realistic User-Agent to try and bypass the antibot
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (X11; Linux x86_64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept": "application/rss+xml,application/xml;q=0.9,*/*;q=0.8"
        }
        
        #xml = requests.get(self.url, timeout=10)
        try:
            response = requests.get(self.url, headers=headers, timeout=10)
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
            #scraper = cloudscraper.create_scraper()
            response = requests.get(self.url, headers=headers, timeout=10)
            print(f"STATUS: {response.status_code}")
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
            body = item["description"]
            success, buzzword = SanitiseArticles.buzzwords_in_title(title)
            if success:
                print(f"BUZZWORD MATCHED ~~ {buzzword} ~~  :  {title}\nDESCRIPTION: {body}")
                id_string = RSSDataCacher.create_id_string(title, item["pub_date"])
                print(f"IDSTR: {id_string}")
                CacheData.cacher(fingerprint=id_string, title=title, source="TheHackerNews")
                #v, p = RSSDataCacher.infer_vendor_product_values(title)
                #print(f"VENDOR:   {v} ::::: PRODUCT:   {p}")
                #data = FingerprintBuilder.build_fingerprint(title, item["pub_date"])
                #print(data)
                
                
            #else:
                #print(f"REDUNDANT ARTICLE: {item["title"]}")            

class CacheData:
    project_root = os.getcwd()
    #arachnid_dir = os.path.join(project_root, "arachnid")
    root_cache = "./cache"
    
    def check_if_exists(self, directory):
        if not os.path.exists(directory):
            print(f"Directory not found... Creating Directory: {directory}")
            full_path = os.path.join(os.getcwd, directory)
            os.makedirs(full_path)

    @classmethod
    def directory_builder(cls, fingerprint):
        parts = fingerprint.split(":")
        dir_path = os.path.join(cls.project_root, "arachnid", "cache", *parts)

        os.makedirs(dir_path, exist_ok=True)
        json_path = os.path.join(dir_path, "articles.json")

        if not os.path.exists(json_path):
            with open(json_path, "w") as f:
                json.dump({"articles": []}, f, indent=2)
        return json_path

        """
        fingerprint = fingerprint.replace(":", "/")
        full_path = os.path.join(str(self.project_root), "arachnid", "cache", str(fingerprint), "articles.json")
        if not os.path.exists(full_path):
            print(f"Directory not found... Creating Directory: {str(full_path)}")
            os.makedirs(str(full_path))
            print(f"Created Directory: {str(full_path)}")
            return full_path
        """
    @staticmethod
    def load_json(json_path):
        with open(json_path, "r") as f:
            return json.load(f)
        
    @staticmethod
    def write_json(json_path, data):
        with open(json_path, "w") as f:
            json.dump(data, f, indent=2)

    @classmethod
    def cacher(cls, fingerprint, title, source="unknown", threshold=85):
        json_path = cls.directory_builder(fingerprint)
        cache = cls.load_json(json_path)
        comparer = TitleComparer()
        cleaned_new = comparer.main(source, title)

        for article in cache["articles"]:
            score = (
                0.5 * fuzz.token_set_ratio(cleaned_new, article["cleaned_title"]) +
                0.3 * fuzz.token_sort_ratio(cleaned_new, article["cleaned_title"]) +
                0.2 * (comparer.jaccard_similarity(cleaned_new, article["cleaned_title"]) * 100)
            )
            if score >= threshold:
                print(f"[CACHE] Duplicate Detected: ({round(score, 2)}%) - SKIPPING")
                return False
        cache["articles"].append({
            "raw_title": title,
            "cleaned_title": cleaned_new,
            "source": source,
            #"ingested": datetime.now(timezone.utc).isoformat()
        })

        cls.write_json(json_path, cache)
        print("[CACHE] New Article Added")
        return True
    
        
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
        id_string = f"{threat_type}:{software_type}:{date}"
        print(f"HEADLINE:   {title}  :  ID string generated:   {id_string}")
        return id_string
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
        

class TitleComparer:
    """Script pipeline:
    1) tokenises each word
    2) removes bloat from the titles
    3) normalises important attributes of each title
    4) orders the set of tokens
    5) converts tokens back to a string
    6) compares titles based on the following algorithms:
        - token set similarity
        - token sort similarity
        - jaccard similarity which looks at the union of two sets of keywords/tokens
        - extracts capitalised words to compare as vendors/products are typically capitaised
            -> bonus score awarded for capitalised values"""


    titles = {
        "BleepingComputer": "IBM warns of critical API Connect auth bypass vulnerability",
        "TheHackerNews": "RondoDox Botnet Exploits Critical React2Shell Flaw to Hijack IoT Devices and Web Servers"
    }
    #words that pad out the titles
    generic_padding_words = {
        "the","a","an","and","or","but","if","while","with","without",
        "to","from","of","on","in","at","by","for","about","as","into",
        "over","after","before","between","through","during","under",
        "above","below","up","down","out","off","again","further",
        "then","once","here","there","when","where","why","how",
        "all","any","both","each","few","more","most","other","some",
        "such","no","nor","not","only","own","same","so","than","too",
        "very","can","will","just","should","now"
    }

    normalisations = {
        "authentication": "auth",
        "authorization": "auth",
        "authorize": "auth",
        "vulnerability": "vuln",
        "flaw": "vuln",
        "bypass": "bypass",
        "extension": "extension",
        "browser": "browser",
        "package": "package",
        "packages": "package",
        "registry": "registry",
        "malicious": "malware",
        "trojan": "malware",
        "worm": "malware",
        "stealer": "malware"
    }

    # lower cases & tokenises each word
    def tokenise_string(self, title):
        title = title.lower()
        return re.findall(r"[a-z0-9\-]+", title)    # use following regex for anything between spaces

    # normalisation method
    def normalise_tokens(self, tokens):
        return [self.normalisations.get(tok, tok) for tok in tokens]

    #strips out generic words
    def strip_out_generic_words(self, tokens):
        return [tok for tok in tokens if tok not in self.generic_padding_words]

    # alphabetically orders strings to assist with fuzzy lookups later
    def order_list(self, tokens):
        return sorted(tokens)

    def create_cleaned_string(self, list):
        string = " ".join(str(word) for word in list)
        return string

    def main(self, source, title):
        tokens = self.tokenise_string(title)
        tokens = self.normalise_tokens(tokens)
        tokens_stripped = self.strip_out_generic_words(tokens)
        ordered_tokens = self.order_list(tokens_stripped)
        new_string = self.create_cleaned_string(ordered_tokens)
        
        print(f"{source}:  {ordered_tokens}")
        print(f"FORGED STRING: {new_string}")
        return new_string
        
    def extract_capitalised_entities(self, title):
        generic_capped_words = {"The", "A", "An", "And", "Or", "But", "To", "Of", "In"}
        entities = set()
        
        for match in re.findall(r"\b(?:[A-Z][a-z0-9]+(?:-[A-Z][a-z0-9]+)*)(?:\s+[A-Z][a-z0-9]+(?:-[A-Z][a-z0-9]+)*)*", title):
            words = match.split()
            if words[0] not in generic_capped_words:
                entities.add(match)
        
        # for entities that are all caps eg NPM, IBM, AWS etc...
        for match in re.findall(r"\b[A-Z]{2,}\b", title):
            entities.add(match)
            
        return entities
        
    #print(strip_out_generic_words(tokenise_string(title)))


    # ========== FUZZY SEARCHING SECTION ============= #

    def score_capitalised_entity_overlap(self, entities_a, entities_b, boost=10):
        matches = entities_a & entities_b
        return len(matches) * boost, matches


    def fuzzy_scoring(self, title1, title2, raw_title1, raw_title2):
        #print(f"SIMILARITY SCORE: {fuzz.token_set_ratio(heading1, heading2)}")
        base_score = (
            0.5 * fuzz.token_set_ratio(title1,title2) +
            0.3 * fuzz.token_sort_ratio(title1, title2) +
            0.2 * (self.jaccard_similarity(title1,title2) * 100)
        )
        entries1 = self.extract_capitalised_entities(raw_title1)
        entries2 = self.extract_capitalised_entities(raw_title2)
        
        boost, matches = self.score_capitalised_entity_overlap(entries1, entries2, boost=15)
        
        final_score = base_score + boost
        
        print(f"BASE SCORE: {round(base_score,2)}")
        print(f"ENTITY MATCHES: {matches}")
        print(f"BOOST: +{boost}")
        print(f"FINAL SCORE: {final_score}")

    # ========== Jacard similarity =========== # 

    def jaccard_similarity(self, a, b):
        set_a = set(a.split())
        set_b = set(b.split())
        
        if not set_a or not set_b:
            return 0.0
        return len(set_a & set_b) / len(set_a | set_b)

    def runner(self):
        headers = []
        raw_titles = []
        
        for name, title in self.titles.items():
            raw_titles.append(title)
            headers.append(self.main(name, title))
        
        self.fuzzy_scoring(headers[0], headers[1], raw_titles[0], raw_titles[1])

   
if __name__=="__main__":
    #parse = RSSParser("https://www.bleepingcomputer.com/feed/")
    parse = RSSParser("https://feeds.feedburner.com/TheHackersNews")
    parse.handle_xml()
    