from datetime import datetime

class ArticleClassifier:
    vulnerability_indicators = ["vulnerability",
                                "flaw",    
                                "cve",
                                "cvss",
                                "bypass",
                                "rce",
                                "remote code execution",
                                "unauthenticated",
                                "authentication bypass"
        ]
    malware_indicators = ["malware",
                          "worm",
                          "trojan",
                          "stealer",
                          "rat",
                          "backdoor",
                          "spyware",
                          "botnet",
                          "loader",
                          "payload"]
    
    software_types = {
        "npm": {
            "indicators": ["npm", "node", "js", "package", "registry", "javascript", "repository"],
            "weight": 1
            },
                        
        "python": {
            "indicators": ["python", "pypi", "pip", "wheel", "egg"],
            "weight": 1
        },
        
        "golang": {
            "indicators": ["golang", "go", "go module", "go package", "go.mod"],
            "weight": 1
        },
        
        "nuget": {
            "indicators": ["nuget", "dotnet", ".net", "c#"],
            "weight": 1
        },
        
        "maven": {
            "indicators": ["maven", "java", "pom.xml", "mvn", "mvnrepository"],
            "weight": 1
        },
        
        "docker": {
            "indicators": ["docker", "image", "dockerfile", "container"],
            "weight": 1
        },
        
        "browser-extension": {
            "indicators": ["browser", "chrome", "extension", "addon", "firefox", "edge"],
            "weight": 1
        },
        
        "unknown": {
            "indicators": [""],
            "weight": 1
        },
    }
    
    @classmethod
    def threat_type(cls, title):
        title = title.lower()
        if any(word in title for word in cls.vulnerability_indicators):
            return "V"
        if any(word in title for word in cls.malware_indicators):
            return "M"
        return "U"
    
    @staticmethod
    def date_stamp(pubdate):
        dt = datetime.strptime(pubdate,"%a, %d %b %Y %H:%M:%S %z")
        return dt.strftime("%d%m%Y")
    
    @classmethod
    def software_type(cls, title):
        title = title.lower()
        for name, data in cls.software_types.items():
            if any(word in title for word in data["indicators"]):
                return name
        return "unknown"
    
    @classmethod
    def fingerprint(cls, title, pubdate):
        return f"{cls.threat_type(title)}:{cls.software_type(title)}:{cls.date_stamp(pubdate)}"