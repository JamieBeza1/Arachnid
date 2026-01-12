import json, os, logging
from arachnid.logger import get_logger
from arachnid.comparer import TitleComparer

logger = get_logger(__name__, logging.DEBUG)

keyword_index_path = os.path.join(os.getcwd(), "arachnid", "cache", "keyword_index.json")

class Cache:
    # root of the cache directory
    root = os.path.join(os.getcwd(), "arachnid", "cache")
    
    @classmethod
    def check_cache(cls, fingerprint):
        # splits fingerprint up by : delimeter
        parts = fingerprint.split(":")
        # creates directory from parts
        path = os.path.join(cls.root,*parts)
        os.makedirs(path, exist_ok=True)
        logger.debug(f"Cache directory found at: {path}")
        
        # creates json file from the path
        json_path = os.path.join(path, "articles.json")
        if not os.path.exists(json_path):
            with open(json_path, "w") as f:
                json.dump({"articles": []}, f, indent=2)
            logger.info(f"Created new cache file at: {json_path}")
        return json_path        
    
    @classmethod
    def exists(cls, fingerprint, title, threshold=80):
        json_path = cls.check_cache(fingerprint)
        with open(json_path, "r") as f:
            cache = json.load(f)

        comparer = TitleComparer()
        cleaned_new = comparer.cleaner(title)

        logger.debug(f"Checking cache for fingerprint: {fingerprint}")

        for article in cache.get("articles", []):
            cleaned_old = article.get("cleaned_title")
            if not cleaned_old:
                cleaned_old = comparer.cleaner(article.get("raw_title", ""))

            score = comparer.scorer(cleaned_new, cleaned_old)
            logger.debug(f"Comparing to cached article: {cleaned_old} (score={score:.2f})")

            if score >= threshold:
                logger.info(f"Duplicate detected for title: {title} (SCORE: {score:.2f}%)")
                return True

        logger.debug(f"No duplicates found for title: {title}")
        return False
    
    @classmethod
    def add_title_to_cache(cls, fingerprint, title, source,link,description,pub_date, keywords):
        # path determined by fingerprint
        json_path = cls.check_cache(fingerprint)
        
        with open(json_path, "r") as f:
            cache = json.load(f)
            
        comparer = TitleComparer()
        cleaned = comparer.cleaner(title)
        
        data = {
            "raw_title": title,
            "cleaned_title": cleaned,
            "link": link,
            "description": description,
            "pub_date": pub_date,
            "source": source,
            "keywords": [keyword.lower() for keyword in (keywords or [])]
        }
        
        cache.setdefault("articles", []).append(data)
        
        # rewrites json back to file
        with open(json_path, "w") as f:
            json.dump(cache, f, indent=2)
        
        cls.add_keywords(fingerprint, data["keywords"])
        
        logger.info(f"Added new article to cached file: {json_path} (DATA: {title})")
        
    @classmethod
    def load_keyword_index(cls):
        os.makedirs(os.path.dirname(keyword_index_path), exist_ok=True)
        if not os.path.exists(keyword_index_path):
            with open(keyword_index_path, "w") as f:
                json.dump({"keywords":{}}, f, indent=2)
        with open(keyword_index_path, "r") as f:
            return json.load(f)
    
    @classmethod
    def save_keyword_index(cls, data):
        with open(keyword_index_path, "w") as f:
            json.dump(data, f, indent=2)
            
    @classmethod
    def keywords_exist(cls, keywords, min_overlap=1):
        # to treturn true if keyword index contains at least min_overlap of the provided keywords
        if not keywords:
            return False
        
        index = cls.load_keyword_index()
        seen = index.get("keywords", {})
        
        overlap = 0
        
        for keyword in set(key.lower() for key in keywords):
            if keyword in seen and seen[keyword]:
                overlap += 1
                if overlap >= min_overlap:
                    return True
        return False
    
    @classmethod
    def add_keywords(cls, fingerprint, keywords):
        if not keywords:
            return
        
        index = cls.load_keyword_index()
        seen = index.setdefault("keywords", {})
        
        for keyword in set(keywords):
            seen.setdefault(keyword, [])
            if fingerprint not in seen[keyword]:
                seen[keyword].append(fingerprint)
                
        cls.save_keyword_index(index)
        