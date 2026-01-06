import requests


class RSSFetcher:
    
    defualt_headers = {
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "application/rss+xml,application/xml;q=0.9,*/*;q=0.8"
    }
    
    @staticmethod
    def looks_like_xml(response):
        content_type = response.headers.get("Content-Type", "").lower()
        if "xml" in content_type:
            return True
        return response.text.lstrip().startswith("<?xml")

    @classmethod
    def fetch(cls, url, timeout=10):
        response = requests.get(url, headers=cls.defualt_headers, timeout=timeout)
        response.raise_for_status()
        if not cls.looks_like_xml(response):
            raise ValueError("Non-XML Response")
        
        return response.content
        