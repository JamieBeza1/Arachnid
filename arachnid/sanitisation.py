class SanitiseArticles:
    # keywords we are looking for:
    buzzwords = [
        "python",
        "golang",
        "npm",
        "node",
        "critical",
        "malware",
        "malicious",
        "rce",
        "remote code execution",
        "arbitrary code execution",
        "10.0",
    ]
        
    @classmethod
    def buzzwords_in_title(clss, title):
        #print(title)
        for buzz in clss.buzzwords: 
            if buzz in title.lower():
                return (True, buzz)
            
        return (False, None)
            