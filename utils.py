import requests
from bs4 import BeautifulSoup

COMPANY_STOP_WORDS = [
    'inc', 'inc.', 'ltd', 'ltd.', 'pty ltd', 'pty ltd.', 'corp', 'corp.',
    'co', 'co.', 'corporation', 'company', 'llc', 'plc', 'gmbh', 'sa', 'ab',
    'bv', 'sarl', 'kg', 'kgaa', 'oy', 'srl', 'spa', 'ag', 'nv', 'ltda', 'pty', 'pty limited',
    'llc', 'limited', 'trust', 'australia', "pty.", "incorporated", "group", "holdings", "services",
    "association", "services", "service"
]


def clean_company_name(company_name):

    company_name_lower = company_name.lower()

    company_name_lower = company_name_lower.replace(',', ' ')

    words = company_name_lower.split()

    filtered_words = [word for word in words if word not in COMPANY_STOP_WORDS]

    cleaned_name = ' '.join(filtered_words)
    return cleaned_name


def scrape_news_content(news_url):
    try:

        response = requests.get(news_url)
        response.raise_for_status()  

        soup = BeautifulSoup(response.content, 'html.parser')
        
        article_content = ""
        for paragraph in soup.find_all('p'):
            article_content += paragraph.get_text() + "\n"

        return article_content

    except requests.exceptions.RequestException as e:
        print(f"Error fetching the news article: {e}")
        return None

    except Exception as e:
        print(f"An error occurred while scraping the content: {e}")
        return None

