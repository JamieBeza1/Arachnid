import logging

from arachnid.logger import get_logger

logger = get_logger(__name__, logging.DEBUG)

class SanitiseArticles:
    # keywords we are looking for:
    buzzwords = [
        "python",
        "golang",
        "npm",
        "node",
        "maven",
        "docker",
        "vscode",
        "critical",
        "malware",
        "malicious",
        "rce",
        "remote code execution",
        "arbitrary code execution",
        "10.0",
        "9."
    ]
        
    @classmethod
    def buzzwords_in_title(clss, title):
        # checks if buzzword is in the title
        for buzz in clss.buzzwords: 
            if buzz in title.lower():
                logger.info(f"Keyword '{buzz.upper()}' found in title: {title}")
                return (True, buzz)
            
        return (False, None)
            