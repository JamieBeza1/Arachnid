import re, logging
from fuzzywuzzy import fuzz
from arachnid.logger import get_logger

logger = get_logger(__name__, logging.DEBUG)


class TitleComparer:
    # list of generic bloat words, should grow over time
    generic_words = {
        "the","a","an","and","or","but","to","of","in","on","for",
        "with","by","from","at","as","is","are","was","were","about","take",
    }
    
    # map for common abreviations/normalisations
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
        
        # tokenises the title by each word & converts to lowercase
        tokens = re.findall(r"[a-z0-9\-]+", title.lower())
        
        # normalises equivilent tokens with a standar form ready for comparison
        tokens = [self.normalisation_map.get(tok, tok) for tok in tokens]
        
        # removes the generic bloat words before comparison
        tokens = [tok for tok in tokens if tok not in self.generic_words]
        
        # sorts and creates string from tokens
        cleaned_title = " ".join(sorted(tokens))
        logger.info(f"Cleaned title: {cleaned_title}")
        return cleaned_title
    
    def scorer(self, a, b):
        # weighted similarity scroe combining fuzzy token matching and jaccard overlap
        base_score = (
            # checks similarity of ordered sets
            0.5 * fuzz.token_set_ratio(a, b) +
            
            # checks ordered string differences on a 1-1 comparison
            0.3 * fuzz.token_sort_ratio(a, b) +
            
            # bonus points awarded for jaccard matches
            0.2 * (self.jaccard_similarity_indexer(a, b) * 100)
        )
        
        logger.info(f"Similarity score between '{a}' and '{b}' = {base_score:.2f}")
        return base_score
        
        
    @staticmethod
    def jaccard_similarity_indexer(a, b):
        # splits strips into sets of unique tokens
        set_a = set(a.split())
        set_b = set(b.split())
        
        # checks if either set is empty
        if not set_a or not set_b:
            logger.debug(f"Jaccard similarity index: One or both sets empty")
            return 0.0
        
        # computes the union/intersection between the sets of tokens
        similarity_index =  len(set_a & set_b) / len(set_a | set_b)
        logger.info(f"Jaccard Similarity Index Score: {similarity_index:.2f}")
        return similarity_index