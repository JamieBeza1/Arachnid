import re
from fuzzywuzzy import fuzz

# -----------------------------
# Stopwords (padding words)
# -----------------------------
STOPWORDS = {
    "the","a","an","and","or","but","if","while","with","without",
    "to","from","of","on","in","at","by","for","about","as","into",
    "over","after","before","between","through","during","under",
    "above","below","up","down","out","off","again","further",
    "then","once","here","there","when","where","why","how",
    "all","any","both","each","few","more","most","other","some",
    "such","no","nor","not","only","own","same","so","than","too",
    "very","can","will","just","should","now",
    "found","warns","issues","alert","flags","using","via"
}

# -----------------------------
# Semantic normalisations
# -----------------------------
NORMALISATIONS = {
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

# -----------------------------
# Normalisation helpers
# -----------------------------
def normalise_text(text: str) -> str:
    text = text.lower()
    for src, dst in NORMALISATIONS.items():
        text = text.replace(src, dst)
    return text


def tokenise(text: str):
    return re.findall(r"[a-z0-9\.\-]+", text)


def strip_stopwords(tokens):
    return [t for t in tokens if t not in STOPWORDS]


def canonicalise(title: str) -> str:
    title = normalise_text(title)
    tokens = tokenise(title)
    tokens = strip_stopwords(tokens)
    tokens.sort()
    return " ".join(tokens)