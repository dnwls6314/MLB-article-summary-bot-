from pynytimes import NYTAPI
from bs4 import BeautifulSoup
import pandas as pd
import requests
import datetime
import warnings 
from pprint import pprint

warnings.filterwarnings(action='ignore')


# Authorize 
nyt = NYTAPI("Your API Key", parse_dates=True)

# Write query 
articles = nyt.article_search(
    query = "baseball",
    results = 100, 
    dates = {
        "begin" : datetime.datetime(2020,1,1),
        "end" : datetime.datetime(2021,12,31)
    },
    options = {
        "sort" : "newest",
        "section_name" :[
            "Sports"
        ]
    }
)

# Save URL of ariticles 
url_list = [news_obj['web_url'] for news_obj in articles]


# Crawling main contents in articles 
results = []
for idx in range(len(url_list)) :
    print('===================={}===================='.format(idx))
    result = []

    html = requests.get(url_list[idx]).content
    soup = BeautifulSoup(html, "lxml")

    result_head = soup.find("h1")
    results_summary = soup.find("p", id="article-summary")
    result_date = soup.find("span", class_="css-1sbuyqj e16638kd3")
    results_article = soup.find_all("p", class_="css-axufdj evys1bk0")

    result.append(result_head.text)
    
    # Some articles does not have summary and date. So make exception.
    try :
        result.append(results_summary.text)
    except :
        result.append(None)

    try : 
        result.append(result_date.text)
    except :
        result.append(None)

    body = ""
    for i in results_article :
        body += i.text
    result.append(body)

    results.append(result)

results = pd.DataFrame(results, columns=['title', 'summary',  'date', 'body'])
results.to_csv('test.csv')
