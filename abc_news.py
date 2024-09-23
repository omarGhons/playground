import json
import os

from database import session_factory
from database.models import GrantCompany, GrantCompanyNew
from utils import clean_company_name

import requests
import os
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import urllib.parse

def abc_search_companies():
    records = session_factory.query(GrantCompany).all()
    path_file = os.path.abspath(os.getcwd())
    
    # Loop through each company record and search ABC for news articles 
    for record in records:
        # Clean the company name
        company_name = record.CompanyName
        
        cleaned_company_name = clean_company_name(record.CompanyName)
        # search ABC for news articles
        print(f"Searching news for: {cleaned_company_name}")
        search_abc_news(cleaned_company_name, record)
        
        
    
        

def search_abc_news(company_name,record, max_pages=1):
    print(f"Searching ABC News for {record.CompanyName}...")
    # Initialize Selenium WebDriver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    
    base_url = 'https://discover.abc.net.au/index.html?siteTitle=news#/?'
    params = {
        'query': f'"{company_name}"'
    }
    query_string = urllib.parse.urlencode(params)
    
    search_url = base_url + query_string
    print(f"Search URL: {search_url}")
    
    driver.get(search_url)
    
    time.sleep(2) 
    
    try:
        search_results = driver.find_elements(By.XPATH, "//div[@data-component='SearchHits']//li")
        
        if search_results:
            for result in search_results:

                title_element = result.find_element(By.TAG_NAME, 'a')
                title = title_element.text
                link = title_element.get_attribute('href')
                
                #open the link and get all the content of the page
                # link www.abc.net.au contains /news/ so we can use the link to get the content of the page
                
                if("/news/" in link):
                    article_content = scrape_news_content(link)
                    print(article_content)
                    print(f"Title: {title}")
                    print(f"Link: {link}")
                    print("-" * 80)
                    if(article_content):
                        new_entry = GrantCompanyNew(
                            CompanyId=record.CompanyId,
                            NewsURL=link,
                            NewsHeader=title,
                            Source="ABC News",
                            NewsContent=article_content
                        )
                        session_factory.add(new_entry)
                        session_factory.commit()
        else:
            print("No results found.")
    
    except Exception as e:
        print(f"An error occurred: {e}")
    
    # Close the browser after scraping
    driver.quit()

def scrape_news_content(news_url):
    try:

        response = requests.get(news_url)
        response.raise_for_status()  

        soup = BeautifulSoup(response.content, 'html.parser')
        
        article_content = ""
        for paragraph in soup.find_all('p', class_='paragraph_paragraph__iYReA'):
            article_content += paragraph.get_text() + "\n"

        return article_content

    except requests.exceptions.RequestException as e:
        print(f"Error fetching the news article: {e}")
        return None

    except Exception as e:
        print(f"An error occurred while scraping the content: {e}")
        return None




abc_search_companies()


