import os
import json
import requests
from bs4 import BeautifulSoup
from sqlalchemy.orm import sessionmaker
import http.client
import config
from database import session_factory
from database.models import GrantCompany, GrantCompanyNew

# Assuming session_factory is defined elsewhere
# session_factory = sessionmaker(bind=engine)

# Define the list of company-related stop words
COMPANY_STOP_WORDS = [
    'inc', 'inc.', 'ltd', 'ltd.', 'pty ltd', 'pty ltd.', 'corp', 'corp.',
    'co', 'co.', 'corporation', 'company', 'llc', 'plc', 'gmbh', 'sa', 'ab',
    'bv', 'sarl', 'kg', 'kgaa', 'oy', 'srl', 'spa', 'ag', 'nv', 'ltda'
]

# Define the list of trusted news sources in Australia
TRUSTED_NEWS_SOURCES = [
    'abc.net.au',
    'sbs.com.au',
    'smh.com.au',
    'theage.com.au',
    'theguardian.com',
    'afr.com',
    'reuters.com',
    'aap.com.au',
    'news.com.au',
    'theaustralian.com.au',
    'brisbanetimes.com.au',
    'canberratimes.com.au',
    'adelaidenow.com.au',
    'themercury.com.au',
    'heraldsun.com.au',
    'couriermail.com.au',
    'dailytelegraph.com.au',
    'westernsydney.edu.au',  # Add more as needed
]

def clean_company_name(company_name):
    # Convert to lowercase for case-insensitive matching
    company_name_lower = company_name.lower()
    # Replace commas with spaces
    company_name_lower = company_name_lower.replace(',', ' ')
    # Split the name into words
    words = company_name_lower.split()
    # Remove stop words
    filtered_words = [word for word in words if word not in COMPANY_STOP_WORDS]
    # Join the words back into a string
    cleaned_name = ' '.join(filtered_words)
    return cleaned_name

def is_trusted_source(url):
    from urllib.parse import urlparse

    domain = urlparse(url).netloc
    # Remove 'www.' prefix if present
    domain = domain.lstrip('www.')
    # Check if the domain ends with any of the trusted domains
    for trusted_domain in TRUSTED_NEWS_SOURCES:
        if domain.endswith(trusted_domain):
            return True
    return False

def search_companies():
    records = session_factory.query(GrantCompany).limit(5).all()
    path_file = os.path.abspath(os.getcwd())

    if config.SERPER_ON == "True":
        for record in records:
            # Clean the company name
            company_name = record.CompanyName
            print(f"Searching news for: {company_name}")
            cleaned_company_name = clean_company_name(company_name)
            safe_company_name = cleaned_company_name.replace('/', '_').replace('\\', '_')
            output_dir = os.path.join(path_file, "news_drop")
            json_file_path = os.path.join(output_dir, f"{safe_company_name}.json")

            # If company name exists in folder, read the JSON file
            if os.path.exists(json_file_path):
                with open(json_file_path, "r") as f:
                    result = json.load(f)
            else:
                result = search_company(cleaned_company_name)

                # Save the result to a JSON file
                os.makedirs(output_dir, exist_ok=True)
                with open(json_file_path, "w") as f:
                    json.dump(result, f)

            result = result.get("news", [])
            print(f"Found {len(result)} articles for {company_name}")
            for item in result:
                news_url = item.get('link', '')
                # Check if the article is from a trusted source
                if not is_trusted_source(news_url):
                    print(f"Skipping untrusted source: {news_url}")
                    continue  # Skip this article

                news_header = item.get('title', '')
                news_content = scrape_news_content(news_url)

                if news_content:
                    new_entry = GrantCompanyNew(
                        CompanyId=record.CompanyId,
                        NewsURL=news_url,
                        NewsHeader=news_header,
                        NewsContent=news_content
                    )
                    session_factory.add(new_entry)
                    session_factory.commit()
                else:
                    print(f"Failed to scrape content from: {news_url}")
    else:
        print("SERPER is turned off. Please turn it on in the .env file.")

def search_company(company_name):
    conn = http.client.HTTPSConnection("google.serper.dev")
    payload = json.dumps({
        "q": company_name
    })
    headers = {
        'X-API-KEY': config.token,
        'Content-Type': 'application/json'
    }
    conn.request("POST", "/news", payload, headers)
    res = conn.getresponse()
    data = res.read()
    return json.loads(data.decode("utf-8"))

def scrape_news_content(news_url):
    try:
        headers = {
            'User-Agent': (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                '(KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
            )
        }
        response = requests.get(news_url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        article_content = ""
        # Target specific containers or fallback to all paragraphs
        content_containers = soup.select('article, div[class*="article"], div[class*="content"], div[class*="entry"]')
        if content_containers:
            for container in content_containers:
                paragraphs = container.find_all('p')
                for paragraph in paragraphs:
                    article_content += paragraph.get_text() + "\n"
        else:
            for paragraph in soup.find_all('p'):
                article_content += paragraph.get_text() + "\n"

        return article_content.strip()

    except requests.exceptions.RequestException as e:
        print(f"Error fetching the news article: {e}")
        return None

    except Exception as e:
        print(f"An error occurred while scraping the content: {e}")
        return None

search_companies()
