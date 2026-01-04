import re
from fuzzywuzzy import fuzz
#from fuzzywuzzy import process

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
def tokenise_string(title):
    title = title.lower()
    return re.findall(r"[a-z0-9\-]+", title)    # use following regex for anything between spaces

# normalisation method
def normalise_tokens(tokens):
    return [normalisations.get(tok, tok) for tok in tokens]

#strips out generic words
def strip_out_generic_words(tokens):
    return [tok for tok in tokens if tok not in generic_padding_words]

# alphabetically orders strings to assist with fuzzy lookups later
def order_list(tokens):
    return sorted(tokens)

def create_cleaned_string(list):
    string = " ".join(str(word) for word in list)
    return string

def main(source, title):
    tokens = tokenise_string(title)
    tokens = normalise_tokens(tokens)
    tokens_stripped = strip_out_generic_words(tokens)
    ordered_tokens = order_list(tokens_stripped)
    new_string = create_cleaned_string(ordered_tokens)
    
    print(f"{source}:  {ordered_tokens}")
    print(f"FORGED STRING: {new_string}")
    return new_string
    
def extract_capitalised_entities(title):
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

def score_capitalised_entity_overlap(entities_a, entities_b, boost=10):
    matches = entities_a & entities_b
    return len(matches) * boost, matches


def fuzzy_scoring(title1, title2, raw_title1, raw_title2):
    #print(f"SIMILARITY SCORE: {fuzz.token_set_ratio(heading1, heading2)}")
    base_score = (
        0.5 * fuzz.token_set_ratio(title1,title2) +
        0.3 * fuzz.token_sort_ratio(title1, title2) +
        0.2 * (jaccard_similarity(title1,title2) * 100)
    )
    entries1 = extract_capitalised_entities(raw_title1)
    entries2 = extract_capitalised_entities(raw_title2)
    
    boost, matches = score_capitalised_entity_overlap(entries1, entries2, boost=15)
    
    final_score = base_score + boost
    
    print(f"BASE SCORE: {round(base_score,2)}")
    print(f"ENTITY MATCHES: {matches}")
    print(f"BOOST: +{boost}")
    print(f"FINAL SCORE: {final_score}")

# ========== Jacard similarity =========== # 

def jaccard_similarity(a,b):
    set_a = set(a.split())
    set_b = set(b.split())
    
    if not set_a or not set_b:
        return 0.0
    return len(set_a & set_b) / len(set_a | set_b)


def runner():
    headers = []
    raw_titles = []
    
    for name, title in titles.items():
        raw_titles.append(title)
        headers.append(main(name, title))
    
    fuzzy_scoring(headers[0], headers[1], raw_titles[0], raw_titles[1])
    
runner()