import requests
from bs4 import BeautifulSoup as bs
from twnews.soup import NewsSoup
import pandas as pd
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

def crawl_news(num):
    news_list = []
    urls = []
    for i in range(num):
        url = 'https://udn.com/news/get_breaks_article/{}/1/99'.format(i+1)
        urls.extend(crawl_page_links(url))

    for l in urls:
        news = {'title':'', 'date_time':'', 'author':'', 'content': '', 'catagoty':'', 'url' : l}
        soup = bs(requests.get(l).text, 'lxml')
        nsoup = NewsSoup(l)
        news['catagoty'] += soup.find(id='nav').find_all('a')[1].get_text()
        news['title'] += nsoup.title()
        news['date_time'] += str(nsoup.date())
        try:
            news['author'] += nsoup.author()
        except:
            news['author'] += 'unknown'
        news['content'] += nsoup.contents()
        news_list.append(news)
    return news_list, urls

def udn_crawler(previous_urls, my_sql_login):
    #Create MySQL connection----    
    engine = create_engine(my_sql_login, encoding='utf-8')
    connection = engine.connect()
    
    #Crawling and inserting to MySQL table----
    news_list, current_url = crawl_news(3)
    
    df = pd.DataFrame(news_list)
    #filter  url not exist in previous urls 
    df = df[~df.url.isin(previous_urls)]
    #Insert to MySQL Table
    if df.shape[0] != 0:
        df.to_sql(name="udn_realtime", con=connection, if_exists='append', index = False)
        print('COMPLETE INSERTING: ' + df['datetime'][df.shape[0]-1])
    else:
        print('NO NEW DATA INSERTED')    

    previous_urls = current_urls
    return previous_urls

#無限looooooooooooooooooooooop
previous_urls = []
my_sql_login = 'mysql+mysqldb://AmoLiu:news_317@140.112.153.64:3306/news?charset=utf8'

while True:
    previous_urls = udn_crawler(previous_urls=previous_urls, my_sql_login=my_sql_login)#appledaily_crawler() 會回傳上一次爬到的url
    
    print('CRAWLER IS SLEEPING')
    time.sleep(7200)