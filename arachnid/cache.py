import json, os
#from fuzzywuzzy import fuzz
from arachnid.comparer import TitleComparer

class Cache:
    root = os.path.join(os.getcwd(), "arachnid", "cache")
    
    @classmethod
    def check_cache(cls, fingerprint):
        parts = fingerprint.split(":")
        path = os.path.join(cls.root,*parts)
        os.makedirs(path, exist_ok=True)
        
        json_path = os.path.join(path, "articles.json")
        if not os.path.exists(json_path):
            with open(json_path, "w") as f:
                json.dump({"articles": []}, f, indent=2)
        
        return json_path        
    
    @classmethod
    def exists(cls, fingerprint, title, threshold=85):
        json_path = cls.check_cache(fingerprint)
        with open(json_path) as f:
            cache = json.load(f)
        
        comparer = TitleComparer()
        cleaned = comparer.cleaner(title)
        
        for article in cache["articles"]:
            score = comparer.scorer(cleaned, article["cleaned_title"])
            if score >= threshold:
                return True
            
        return False
    
    @classmethod
    def add_title_to_cache(cls, fingerprint, title, source):
        json_path = cls.check_cache(fingerprint)
        with open(json_path) as f:
            cache = json.load(f)
            
        comparer = TitleComparer()
        cache["articles"].append({
            "raw_title": title,
            "cleaned_title":comparer.cleaner(title),
            "source": source
        })
        
        with open(json_path, "w") as f:
            json.dump(cache, f, indent=2)