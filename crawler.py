import requests
import xml.etree.ElementTree as ET
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time
from datetime import datetime, timedelta
import re

from reporter import Reporter
from summit import Summary

class Crawler:
    def __init__(self, rss_feed_url):
        self.rss_feed_url = rss_feed_url
        
        self.buzzwords = ["malicious", "Fortinet", "malware", "critical", "vulnerability", " RCE ", "arbitrary", "code execution", "python", "pypi", "infect", "CVE", "go", "npm"]
        self.important_information = ["CVE", "CVSS", "github"]
        self.articles = {}
        
        self.days_back = 1 # change no. of days back to crawl to 
                
        # Selenium config to load pages as a normal browser
        self.options = Options()
        self.options.add_argument("--headless")
        self.options.add_argument("--disable-gpu")
        self.options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36") 
        
        self.driver = webdriver.Chrome(options=self.options)
        
        self.summariser = Summary()

    def extract_date_from_rss(self, pubDate_text):
        try:
            dt = datetime.strptime(pubDate_text, "%a, %d %b %Y %H:%M:%S %z")
            return dt
        except Exception as e:
            print(f"Error parsing RSS pubDate: {e}")
            return None

    def check_date_in_range(self, date_obj):
        now = datetime.now(date_obj.tzinfo)  # to keep timezone consistent
        cutoff_date = now - timedelta(days=self.days_back)
        return date_obj >= cutoff_date

    def parse_rss_feed(self):
        response = requests.get(self.rss_feed_url)
        if response.status_code != 200:
            print(f"Failed to fetch RSS feed: Status {response.status_code}")
            return []
        
        root = ET.fromstring(response.content)
        items = root.findall('.//item')
        
        extracted_articles = []

        for item in items:
            title_elem = item.find('title')
            link_elem = item.find('link')
            pubDate_elem = item.find('pubDate')

            if title_elem is not None and link_elem is not None and pubDate_elem is not None:
                title = title_elem.text.strip()
                link = link_elem.text.strip()
                pubDate = pubDate_elem.text.strip()

                date_obj = self.extract_date_from_rss(pubDate)
                if date_obj and self.check_date_in_range(date_obj):
                    extracted_articles.append((title, link))
                else:
                    print(f"Skipping old article: {title}")
            else:
                print(f"Incomplete RSS item found, skipping...")
        
        return extracted_articles

    def crawl(self):
        articles = self.parse_rss_feed()
        
        for title, link in articles:
            self.check_buzzwords(title, link)
            self.follow_link(link)

    def check_buzzwords(self, title, link):
        matched_buzzwords = [buzz for buzz in self.buzzwords if buzz.upper() in title.upper()]
        
        if matched_buzzwords:
            self.articles[title] = link
            buzz_str = ", ".join(f"\033[31m{buzz}\033[0m" for buzz in matched_buzzwords)
            print(f"Article of Interest: \033[36m{title}\033[0m -- flagged by buzzword(s): {buzz_str}")
        print()    

    def extract_important_article_information(self, article):
        info_found = {}
        
        cve_pattern = r'CVE-\d{4}-\d{4,7}'
        cvss_pattern = r'CVSS(?: score)?:\s?\d\.\d'
        github_pattern = r'(?:https?://)?github\.com/[^\s\'"<>]+'
        
        for info in self.important_information:
            if info == "CVE":
                cves_found = re.findall(cve_pattern, article)
                if cves_found:
                    info_found[info] = cves_found
            elif info == "CVSS":
                cvss_found = re.findall(cvss_pattern, article)
                if cvss_found:
                    info_found[info] = cvss_found
            elif info == "github":
                github_links = re.findall(github_pattern, article)
                if github_links:
                    info_found[info] = github_links
        
        return info_found

    def follow_link(self, link):
        self.driver.get(link)

        content = ""
        summed_content = "No Summary Available for this article"
        important_info = {}

        try:
            WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.ID, "articlebody")))
            content_elem = self.driver.find_element(By.ID, "articlebody")
            content = content_elem.text.strip()

            if content:
                try:
                    important_info = self.extract_important_article_information(content)
                    summed_content = self.summariser.summarise_text(content)
                except Exception as e:
                    print(f"Error summarising content: {e}")
                    summed_content = "Error - No summary available."
            else:
                print(f"Warning: Article content is empty for link: {link}")

        except Exception as se:
            print(f"Error fetching article content: {se}")

        for art in self.articles:
            if self.articles[art] == link:
                self.articles[art] = {
                    "Content": content,
                    "Summary": summed_content,
                    "Important Info": important_info,
                    "link": link,
                    "Original Content": content
                }

    def write_report(self):
        if self.articles:
            reporter = Reporter(self.articles)
            reporter.generate_report()
        else:
            print("No articles found.")

