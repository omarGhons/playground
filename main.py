import http.client
import json

from database import session_factory
from database.models import GrantCompany, GrantCompanyNew
import os

from bs4 import BeautifulSoup
from utils import clean_company_name, scrape_news_content
from abc_news import abc_search_companies
import config
from config import SERPER_TOKEN as token






def serper_search_companies():
    records = session_factory.query(GrantCompany).limit(5).all()
    path_file = os.path.abspath(os.getcwd())
    if(config.SERPER_ON == "True"):       
        for record in records:
            company_name = clean_company_name(record.CompanyName)
            safe_company_name = company_name.replace('/', '_').replace('\\', '_')
            output_dir = path_file + "/news_drop/"
            json_file_path = os.path.join(output_dir, f"{safe_company_name}.json")
            
            #if company name exist in folder continue to next record
            if os.path.exists(json_file_path):
                #read the json file 
                with open(json_file_path, "r") as f:
                    result = json.load(f)
            else:
                result = search_company(company_name)
                
                #save  the result to a json file
                os.makedirs('/news_drop', exist_ok=True)
                with open(json_file_path, "w") as f:
                    json.dump(result, f)
                 
            result = json.loads(result)
            result = result["news"]
            print(result)
            for item in result:
                new_entry = GrantCompanyNew(
                CompanyId=record.CompanyId,  
                NewsURL=item.get('link', ''),  
                NewsHeader=item.get('title', ''),  
                NewsContent = scrape_news_content(item['link'])
                )
                session_factory.add(new_entry)
                session_factory.commit()   
    else:
        print("SERPER is turned off. Please turn it on in the .env file.")
        
    

def search_company(company_name):
    conn = http.client.HTTPSConnection("google.serper.dev")
    payload = json.dumps({
        "q": company_name
    })
    headers = {
        'X-API-KEY': token,
        'Content-Type': 'application/json'
    }
    conn.request("POST", "/news", payload, headers)
    res = conn.getresponse()
    data = res.read()
    return data.decode("utf-8")




# serper_search_companies()

abc_search_companies()