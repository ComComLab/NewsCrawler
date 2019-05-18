import requests
from bs4 import BeautifulSoup as bs
from twnews.soup import NewsSoup
import pandas as pd
import MySQLdb
from sqlalchemy import create_engine
import time
import sys
#%%
def crawl_links_and_cat(url):
    soup = bs(requests.get(url).text, 'lxml')
    links = []
    url_a = soup.find_all(class_='tit')
    for h in url_a :
        if 'https:' in h['href']:
            links.append(h['href'])
        else:
            links.append('https:'+h['href'])
    category_all = soup.find_all('div', 'tagarea')
    category_list = [c.find('a').get_text() for c in category_all]
    
    links_cat_dict = dict((a, b) for a, b in zip(links, category_list) if b != "")
    return links_cat_dict

def ltn_crawler(my_sql_login):
    try:
        #Create MySQL connection----    
        engine = create_engine(my_sql_login, encoding='utf-8')
        connection = engine.connect()    
        
        query = 'SELECT url FROM ltn_realtime ORDER BY datetime DESC LIMIT 500'
        result_proxy = connection.execute(query)
        previous_urls = [u for u,  in result_proxy.fetchall()]
       #Crawling and inserting to MySQL table----
        for i in range(5):
            url = 'https://news.ltn.com.tw/list/breakingnews/all/{}'.format(i+1)
            url_and_category = crawl_links_and_cat(url)
            
            for l, c in url_and_category.items():
                if l not in previous_urls:
                    news = {'title':'', 'datetime':'', 'content': '', 'category': c, 'url': l}
                    nsoup = NewsSoup(l)    
                    news['title'] += nsoup.title()
                    news['datetime'] += str(nsoup.date())
                    news['content'] += nsoup.contents()
                    
                    df = pd.DataFrame(news, index = [1]) 
                    df.to_sql(name="ltn_realtime", con=connection, if_exists='append', index = False)
                    print('COMPLETE INSERTING: ' + str(nsoup.date()))
                 
                else:
                    print('NO NEW DATA INSERTED')  
    except:
            print("Unexpected error:", sys.exc_info()[0])

#無限looooooooooooooooooooooop
my_sql_login = 'mysql+mysqldb://AmoLiu:news_317@140.112.153.64:3306/news?charset=utf8'

while True:
    ltn_crawler(my_sql_login)
    
    print('------CRAWLER IS SLEEPING------')
    time.sleep(7200)


