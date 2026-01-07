import re, logging
from fuzzywuzzy import fuzz
from arachnid.logger import get_logger

logger = get_logger(__name__, logging.DEBUG)


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
        logger.debug(f"Cleaning title: {title}")
        tokens = re.findall(r"[a-z0-9\-]+", title.lower())
        tokens = [self.normalisation_map.get(tok, tok) for tok in tokens]
        tokens = [tok for tok in tokens if tok not in self.generic_words]
        cleaned_title = " ".join(sorted(tokens))
        logger.info(f"Cleaned title: {cleaned_title}")
        return cleaned_title
    
    def scorer(self, a, b):
        base_score = (
            0.5 * fuzz.token_set_ratio(a, b) +
            0.3 * fuzz.token_sort_ratio(a, b) +
            0.2 * (self.jaccard_similarity_indexer(a, b) * 100)
        )
        logger.info(f"Similarity score between '{a}' and '{b}' = {base_score:.2f}")
        return base_score
        
    @staticmethod
    def jaccard_similarity_indexer(a, b):
        set_a = set(a.split())
        set_b = set(b.split())
        
        if not set_a or not set_b:
            logger.debug(f"Jaccard similarity index: One or both sets empty")
            return 0.0
        similarity_index =  len(set_a & set_b) / len(set_a | set_b)
        logger.info(f"Jaccard Similarity Index Score: {similarity_index:.2f}")
        return similarity_index