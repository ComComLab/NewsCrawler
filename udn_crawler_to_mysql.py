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

def udn_crawler(my_sql_login):
    try:
        #Create MySQL connection----    
        engine = create_engine(my_sql_login, encoding='utf-8')
        connection = engine.connect()
        query = 'SELECT url FROM udn_realtime ORDER BY datetime DESC LIMIT 500'
        result_proxy = connection.execute(query)
        previous_urls = [u for u,  in result_proxy.fetchall()]
        
        #Crawling and inserting to MySQL table----
        current_urls = []
        for i in range(5):
            url = 'https://udn.com/news/get_breaks_article/{}/1/99'.format(i+1)
            current_urls.extend(crawl_page_links(url))

            for l in current_urls:
                if l not in previous_urls:
                    news = {'title':'', 'datetime':'', 'content': '', 'catagoty':'', 'url' : l}
                    soup = bs(requests.get(l).text, 'lxml')
                    nsoup = NewsSoup(l)
                    news['title'] += nsoup.title()
                    news['catagoty'] += soup.find(id='nav').find_all('a')[1].get_text()
                    news['datetime'] += str(nsoup.date())
                    news['content'] += nsoup.contents()
                    
                    df = pd.DataFrame(news, index = [1])
                    df.to_sql(name="udn_realtime", con=connection, if_exists='append', index = False)
                    print('COMPLETE INSERTING: ' + str(nsoup. date()))
                else:
                    print('NO NEW DATA INSERTED')   
        
    except:
            print("Unexpected error:", sys.exc_info()[0])
#無限looooooooooooooooooooooop
my_sql_login = #enter your login
while True:
    udn_crawler(my_sql_login=my_sql_login)
    
    print('------CRAWLER IS SLEEPING------')
    time.sleep(7200)
