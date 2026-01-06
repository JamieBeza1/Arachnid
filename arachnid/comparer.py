import re
from fuzzywuzzy import fuzz

class TitleComparer:
    generic_words = {
        "the","a","an","and","or","but","to","of","in","on","for",
        "with","by","from","at","as","is","are","was","were"
    }
    
    normalisation_map = {
        "authentication": "auth",
        "authorization": "auth",
        "vulnerability": "vuln",
        "flaw": "vuln",
        "malicious": "malware",
        "trojan": "malware",
        "worm": "malware",
        "stealer": "malware"
    }
    
    def cleaner(self, title):
        tokens = re.findall(r"[a-z0-9\-]+", title.lower())
        tokens = [self.normalisation_map.get(tok, tok) for tok in tokens]
        tokens = [tok for tok in tokens if tok not in self.generic_words]
        return " ".join(sorted(tokens))
    
    def scorer(self, a, b):
        return (
            0.5 * fuzz.token_set_ratio(a, b) +
            0.3 * fuzz.token_sort_ratio(a, b) +
            0.2 * (self.jaccard_similarity_indexer(a, b) * 100)
        )
        
    @staticmethod
    def jaccard_similarity_indexer(a, b):
        set_a = set(a.split())
        set_b = set(b.split())
        
        if not set_a or not set_b:
            return 0.0
        return len(set_a & set_b) / len(set_a | set_b)