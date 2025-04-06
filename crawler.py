#import requests
#from bs4 import BeautifulSoup

#nned to use selenium, not bs4 as bs4 gets blocked by js based anti-bot  systems. selenium bypasses this as loads pages like an actual browser
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from reporter import Reporter
from summit import Summary

class Crawler:
    def __init__(self,url):
        self.url = url
        
        self.buzzwords = ["malicious", "malware", "critical", "vulnerability", "RCE", "arbitrary", "code execution", "python", "pypi", "infect", "CVE", ]
        self.articles = {}
        
        #selenium configuration
        self.options = Options()
        self.options.add_argument("--headless")
        self.options.add_argument("--disable-gpu")
        self.options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36") # mimincs real browser user agent string
        
        self.driver = webdriver.Chrome(options=self.options)
        
        #import of summariser model
        self.summariser = Summary()
    

    def crawl_and_extract_h2s(self, element_class_name):    
        self.driver.get(self.url)
        articles = self.driver.find_elements(By.CLASS_NAME, 'story-link')
        
        extracted_articles = []
        unique_articles = set()
        
        for article in articles:
            try:
                title =article.find_element(By.CLASS_NAME, element_class_name) # class name to be removed and replace with parameter for maximum code reusabbility
                link = article.get_attribute("href")
                article_tuple = (title.text.strip(), link.strip())
                
                if article_tuple not in unique_articles and all(article_tuple):
                    extracted_articles.append(article_tuple)
                    unique_articles.add(article_tuple)
                    #self.check_buzzwords(title, link)
                    #self.follow_link(link)
            except Exception as e:
                print(f"Error extracting article: {e}")
        
        #check each article for buzzwords and follow links
        for title,link in extracted_articles:
            self.check_buzzwords(title, link)
            self.follow_link(link)
        #print(extracted_articles)
    
    def check_buzzwords(self, title, link):
        matched_buzzwords = [buzz for buzz in self.buzzwords if buzz.upper() in title.upper()]
        
        if matched_buzzwords:
            self.articles[title] = link
            buzz_str = ", ".join(f"\033[31m{buzz}\033[0m" for buzz in matched_buzzwords)
            print(f"Article of Interest: \033[36m{title}\033[0m -- flagged by buzzword(s): {buzz_str}")
        print()    
                
    def follow_link(self, link):
        self.driver.get(link)

        # Define content and summary early so they’re always available
        content = ""
        summed_content = "No Summary Available for this article"

        try:
            WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.ID, "articlebody")))
            content_elem = self.driver.find_element(By.ID, "articlebody")
            content = content_elem.text.strip()
            #print(f"\nCONTENT:\n{content}")

            if content:
                try:
                    summed_content = self.summariser.summarise_text(content)
                    #print(f"\nSUMMED CONTENT:\n{summed_content}")
                except Exception as e:
                    print(f"Error summarising content: {e}")
                    summed_content = "Error - No summary available."
            else:
                print(f"Warning: Article content is empty for link: {link}")

        except Exception as se:
            print(f"Error fetching article content: {se}")
            # content and summed_content already defaulted above

        # Update the article dictionary outside the try/except blocks
        for art in self.articles:
            if self.articles[art] == link:
                self.articles[art] = {"Content": content, "Summary": summed_content}

                
    
    def write_report(self):
        if self.articles:
            reporter = Reporter(self.articles)
            reporter.generate_report()
        else:
            print("No articles found.")
