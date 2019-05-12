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


def chinatimes_crawler(previous_urls, my_sql_login):
    #Create MySQL connection----    
    engine = create_engine(my_sql_login, encoding='utf-8')
    connection = engine.connect()
    
    current_urls = []
    for i in range(3): #一次爬3頁
        try:
            pre_url = 'https://www.chinatimes.com/realtimenews/?page={}chdtv' 
            
            req = requests.get(pre_url.format(i))
            
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
                               'classification': classification,
                               'content':content,  
                               'source': 'Chinatimes'})
                
                     #filter  url not exist in previous urls 
            df = df[~df.url.isin(previous_urls)]
            
            #Insert to MySQL Table
            if df.shape[0] != 0:
                df.to_sql(name="chinatimes_realtime", con=connection, if_exists='append', index = False)
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
    
    print('CRAWLER IS SLEEPING')
    time.sleep(7200)