## Test file to run PoC scripts on before integration
import trafilatura
import requests
#import xml.etree.ElementTree as ET

"""
NOTES
next steps looking at integrating with ai
when AI parses it it should extract vendor/product/version
these details should then be added to the cache object and run more indepth checks aginst the article about ot be added

what should the AI receive:
title
description

what output is expected:
any CVE details
name of software
vendor of software
software version

"""
url = "https://krebsonsecurity.com/feed/"
headers = {
            "User-Agent": (
                "Mozilla/5.0 (X11; Linux x86_64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept": "application/rss+xml,application/xml;q=0.9,*/*;q=0.8"
        }

def get(url):
    xml = requests.get(url, headers, timeout=10)
    return xml



print(get(url=url))