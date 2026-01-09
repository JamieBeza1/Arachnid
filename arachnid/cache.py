import json, os, logging
from arachnid.logger import get_logger
from arachnid.comparer import TitleComparer

logger = get_logger(__name__, logging.DEBUG)

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
        with open(json_path) as f:
            cache = json.load(f)
        # inits comparer class to run checks with
        comparer = TitleComparer()
        cleaned = comparer.cleaner(title)

        logger.debug(f"Checking cache for fingerprint: {fingerprint}")
        
        for article in cache["articles"]:
            # creates a score from the comparer scripts
            to_compare_with = comparer.cleaner(article["title"])
            score = comparer.scorer(cleaned, to_compare_with)
            logger.debug(f"Comparing to cached article: {to_compare_with}")
            # checks if similarity score is above threshold
            if score >= threshold:
                logger.info(f"Duplicate detected for title: {title} (SCORE: {score}%)")
                return True
        logger.debug(f"No Duplicates found for title: {title}") 
        return False
    
    @classmethod
    def add_title_to_cache(cls, fingerprint, title, source,link,description,pub_date):
        # path determined by fingerprint
        json_path = cls.check_cache(fingerprint)
        with open(json_path) as f:
            cache = json.load(f)
            
        #comparer = TitleComparer()
        # appends new titles to json loaded
        cache["articles"].append({
            "title": title,
            "link": link,
            "description": description,
            "pub_date": pub_date,
            "source": source
        })
        
        # rewrites json back to file
        with open(json_path, "w") as f:
            json.dump(cache, f, indent=2)
        logger.info(f"Added new article to cached file: {json_path} (DATA: {title})")