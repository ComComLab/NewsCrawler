import requests
from bs4 import BeautifulSoup as bs
from twnews.soup import NewsSoup
import pandas as pd
import MySQLdb
from sqlalchemy import create_engine
import time
import sys

#%%
def crawl_page_links(url):
    soup = bs(requests.get(url).text, 'lxml')
    links = []
    prefix = 'https://udn.com'
    a = soup.find_all('dt')
    for h in a :
        try:
            if h.a['href'][-4:] == 'news':
                links.append(prefix + h.a['href'])
        except:
            pass
    return links

def udn_crawler(previous_urls, my_sql_login):
    try:
        #Create MySQL connection----    
        engine = create_engine(my_sql_login, encoding='utf-8')
        connection = engine.connect()
        
        #Crawling and inserting to MySQL table----
        current_urls = []
        for i in range(2):
            url = 'https://udn.com/news/get_breaks_article/{}/1/99'.format(i+1)
            current_urls.extend(crawl_page_links(url))

        for l in current_urls:
            if l not in previous_urls:
                news = {'title':'', 'date_time':'', 'content': '', 'catagoty':'', 'url' : l}
                soup = bs(requests.get(l).text, 'lxml')
                nsoup = NewsSoup(l)
                news['title'] += nsoup.title()
                news['catagoty'] += soup.find(id='nav').find_all('a')[1].get_text()
                news['date_time'] += str(nsoup.date())
                news['content'] += nsoup.contents()
                
                df = pd.DataFrame(news, index = [1])
                df.to_sql(name="udn_realtime", con=connection, if_exists='append', index = False)
                print('COMPLETE INSERTING: ' + str(nsoup.date()))
            else:
                print('NO NEW DATA INSERTED')   
        
    except:
            print("Unexpected error:", sys.exc_info()[0])
    previous_urls = current_urls
    return previous_urls

#無限looooooooooooooooooooooop
previous_urls = []
my_sql_login = 'mysql+mysqldb://AmoLiu:news_317@140.112.153.64:3306/news?charset=utf8'

while True:
    previous_urls = udn_crawler(previous_urls=previous_urls, my_sql_login=my_sql_login)#appledaily_crawler() 會回傳上一次爬到的url
    
    print('CRAWLER IS SLEEPING')
    time.sleep(7200)