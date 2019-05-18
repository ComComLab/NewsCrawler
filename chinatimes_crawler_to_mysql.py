# -*- coding: utf-8 -*-
"""
Created on Sun May 12 18:47:05 2019

@author: user
"""
from twnews.soup import NewsSoup
import requests
from bs4 import BeautifulSoup
import pandas as pd
import MySQLdb
from sqlalchemy import create_engine
import sys
import time


def chinatimes_crawler(my_sql_login):
    #Create MySQL connection----    
    engine = create_engine(my_sql_login, encoding='utf-8')
    connection = engine.connect()
    query = 'SELECT url FROM chinatimes_realtime ORDER BY datetime DESC LIMIT 500; '
    result_proxy = connection.execute(query)
    previous_urls = [u for u,  in result_proxy.fetchall()]
    
    for i in range(6): #一次爬6頁
        try:
            pre_url = 'https://www.chinatimes.com/realtimenews/?page={}'            
            req = requests.get(pre_url.format(i+1))
            
            #get url and classification                       
            doc = req.text
            soup = BeautifulSoup(doc, 'html.parser')
                                    
            url_a = soup.select('h3.title a')
            url = ['https://www.chinatimes.com' + a['href'] for a in url_a]
                        
            classification_a = soup.select('div.category a')
            classification = [a.get_text() for a in classification_a]
            
            #get title, date, and content using twnews              
            news_soups = [NewsSoup(u) for u in url]
            
            title = [soup.title() for soup in news_soups]
            datetime = [soup.date() for soup in news_soups]
            content = [soup.contents() for soup in news_soups]

            df = pd.DataFrame({'title': title,
                               'datetime': datetime,
                               'url': url,
                               'catagoty': classification,
                               'content':content})
                
                     #filter  url not exist in previous urls 
            df = df[~df.url.isin(previous_urls)]
            
            #Insert to MySQL Table
            if df.shape[0] != 0:
                df.to_sql(name="chinatimes_realtime", con=connection, if_exists='append', index = False)
                print('COMPLETE INSERTING ' + str(df.shape[0]) + ' ROWS: ' + str(df['datetime'][df.shape[0]-1]))
            else:
                print('NO NEW DATA INSERTED')
            
        except:
            print("Unexpected error:", sys.exc_info()[0])

#無限looooooooooooooooooooooop
previous_urls = []
my_sql_login = 'mysql+mysqldb://AmoLiu:news_317@140.112.153.64:3306/news?charset=utf8'

while True:
    chinatimes_crawler(my_sql_login)
    
    print('------CRAWLER IS SLEEPING------')
    time.sleep(7200)