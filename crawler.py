# crawling 
from pynytimes import NYTAPI
from bs4 import BeautifulSoup
import requests

# save crawled data  
import pandas as pd
import os
import pickle 

# ETC
import datetime
import warnings 
from tqdm import tqdm 

warnings.filterwarnings(action='ignore')


# write and send qeury 
# get data from web page 
def send_qeury(qeury, start, end) : 
    articles = nyt.article_search(
        query = qeury, 
        results = 1000,
        dates = {
            "begin" : start,
            "end" : end
        },
        options = {
            "sort" : "oldest",
            "section_name" :[
                "Sports"
            ]
        }
    )

    return articles



# Organize the urls of articles for the requested query
# Afterwards, organize the urls to use for crawling the body
def get_data_from_api(articles) : 
    urls, ids = [], []
    for news_obj in articles :
        urls.append(news_obj['web_url'])
        ids.append(news_obj['_id']) 
    
    return urls, ids


def date_delta(start, end) :
    time_container = [] 
    i = 0
    temp = start
    time_container.append(start)

    while True :
        if temp == end :
            break

        temp += datetime.timedelta(days=1)
        i += 1
        
        if temp.day == 1 :
            time_container.append(temp) 

    return time_container




if __name__ == "__main__" : 

    # Authorize 
    nyt = NYTAPI("Your API Key", parse_dates=True)

    # read previous csv file
    if os.path.isfile("data/data.pickle") :
        with open("data/data.pickle", "rb") as f :
            data = pickle.load(f)
        previous_id = list(data.id)

    else :
        previous_id = []
    
    # Set date
    start_date = datetime.date(2021, 1, 1)
    end_date = datetime.date(2022, 1, 1)
    timelist = date_delta(start_date, end_date)

    # Save URL of ariticles 
    results = []
    for date_idx, _ in enumerate(timelist) : 
        if date_idx == len(timelist)-1 :
            break
        
        print('crawling processed ------------ {}/{}/{} - {}/{}/{}'.format(timelist[date_idx].year, timelist[date_idx].month, timelist[date_idx].day, timelist[date_idx+1].year, timelist[date_idx+1].month, timelist[date_idx+1].day))
        article_object = send_qeury("baseball", timelist[date_idx], timelist[date_idx+1])
        url_list, id_list = get_data_from_api(article_object)

        # if data has been collected before, pass it 
        if id_list[-1] in previous_id : 
            print("pass")
            continue

        # Crawling main contents in articles 
        for idx in range(len(url_list)) :
            result = []

            result.append(id_list[idx])

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


    results = pd.DataFrame(results, columns=['id', 'title', 'summary',  'date', 'body'])
    
    # if there is previous data, append it 
    if os.path.isfile("data/data.pickle") : 
        results = data.append(results)

    with open('data/data.pickle', 'wb') as f:
        pickle.dump(results, f)
    print("Finish crawling")
