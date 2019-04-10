# -*- coding: utf-8 -*-
"""
appledaily_crawler_to_my_sql
"""
import requests
from bs4 import BeautifulSoup
import pandas as pd
import MySQLdb
from sqlalchemy import create_engine
import sys
import time

df_list = []

def appledaily_crawler(previous_urls, my_sql_login):
    #Create MySQL connection----    
    engine = create_engine(my_sql_login, encoding='utf-8')
    connection = engine.connect()
    
    #Crawling and inserting to MySQL table----
    current_urls = []
    for i in range(4): #一次爬4頁
        try:
            pre_url = 'https://tw.appledaily.com/new/realtime/'
            
            req = requests.get(url = pre_url + str(i))
                            
            doc = req.text
            soup = BeautifulSoup(doc, 'html.parser')
            
            
            title_h1 = soup.select('ul.rtddd.slvl h1')
            title = [h1.get_text() for h1 in title_h1]
            
            classification_h2 = soup.select('ul.rtddd.slvl h2')
            classification = [h2.get_text() for h2 in classification_h2]
            
            url_a = soup.select('ul.rtddd.slvl a')
            url = [a['href'] for a in url_a]
            
            all_content = []
            all_datetime = []
            for u in url:
                try:
                    req_contnet = requests.get(url = u)    
                    doc_content = req_contnet.text
                    soup_content = BeautifulSoup(doc_content, 'html.parser')
                
                    
                    content_p = soup_content.select('div.ndArticle_contentBox > article > div > p ')[0]
                    text = content_p.get_text()
                    content = text.split('看了這則新聞的人，也看了')[0]
                   
                    datetime_div = soup_content.find('div', 'ndArticle_creat')
                    datetime_text = datetime_div.get_text()
                    datetime = datetime_text.split('出版時間：')[1]    
                    
                    all_content.append(content)
                    all_datetime.append(datetime)
                    
                    current_urls.append(u)

                except:
                    print("Unexpected error:", sys.exc_info()[0])
                
            df = pd.DataFrame({'title': title,
                               'datetime': all_datetime,
                               'url': url,
                               'classification': classification,
                               'content':all_content,  
                               'source': 'AppleDaily'})

            #filter  url not exist in previous urls 
            df = df[~df.url.isin(previous_urls)]
            
            #Insert to MySQL Table
            if df.shape[0] != 0:
                df.to_sql(name="appledaily_sample", con=connection, if_exists='append', index = False)
                print('COMPLETE INSERTING: ' + df['datetime'][df.shape[0]-1])
            else:
                print('NO NEW DATA INSERTED')
            
        except:
            print("Unexpected error:", sys.exc_info()[0])
    #set previous urls
    previous_urls = current_urls
    return previous_urls

#無限looooooooooooooooooooooop
previous_urls = []
my_sql_login = 'mysql+mysqldb://AmoLiu:news_317@140.112.153.64:3306/news?charset=utf8'

while True:
    previous_urls = appledaily_crawler(previous_urls=previous_urls, my_sql_login=my_sql_login)#appledaily_crawler() 會回傳上一次爬到的url
    
    print('------CRAWLER IS SLEEPING------')
    time.sleep(7200)
    
