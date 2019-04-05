# -*- coding: utf-8 -*-
"""
Ettoday crawler to MySQL
"""
import requests
from bs4 import BeautifulSoup
import pandas as pd
import MySQLdb
from sqlalchemy import create_engine
import time
import sys

def ettoday_crawler(previous_urls, my_sql_login):
    #Create MySQL connection----    
    engine = create_engine(my_sql_login, encoding='utf-8')
    connection = engine.connect()    
 
    #Crawling and inserting to MySQL table----
    current_urls = []
    for i in range(1, 50): #一次爬500篇
        try:
            req = requests.post(
                    url = 'https://www.ettoday.net/show_roll.php',
                    data = {'offset': i, #一次爬10篇
                            'tPage': 3,  #不知道是啥              
                            'tFile': today_date + '.xml', #tFile = 當天日期.xml
                            'tOt': 0,
                            'tSi': 100, #不知道是啥
                            'tAr': 0
                            },
                        )
            #get url, title, date, classification
            doc = req.text
            soup = BeautifulSoup(doc, 'html.parser')
            
            date_span = soup.find_all('span', 'date')
            date = [span.get_text() for span in date_span]
            
            title_a = soup.find_all('a')
        
            title = [a.get_text() for a in title_a]
                        
            classification_em = soup.find_all('em')
            classification = [em.get_text() for em in classification_em]    
            
            all_content = []
            url = ['https://www.ettoday.net'+ a.get('href') for a in title_a]
            for u in url:
                try:
                    req_contnet = requests.get(url = u)    
                    doc_content = req_contnet.text
                    soup_content = BeautifulSoup(doc_content, 'html.parser')
                        
                    #粗體字為圖片的文字拿掉 
                    contnet_p_invalid = soup_content.find_all(lambda tag: tag.name == 'strong')
                    content_invalid = [p.get_text() for p in contnet_p_invalid]
                        
                    content_p = soup_content.select('.story > p')
                    content = [p.get_text() for p in content_p if p.get_text() not in content_invalid]
                    #把每段文字join起來    
                    content_join  = '/n'.join(content)
                        
                    all_content.append(content_join)
                    current_urls.append(u)
                except:
                    print("Unexpected error:", sys.exc_info()[0])
                
            df = pd.DataFrame({'datetime': date,
                               'title': title,
                               'url': url,
                               'classification': classification,
                               'content': all_content,
                               'source': 'Ettoday'})
            #filter  url not exist in previous urls 
            #這只能判斷跟上次500篇是否重複！！！
            df = df[~df.url.isin(previous_urls)]
            
            #Insert to MySQL Table
            if df.shape[0] != 0:
                df.to_sql(name="ettoday_sample", con=connection, if_exists='append', index = False)
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
    previous_urls = ettoday_crawler(previous_urls=previous_urls, my_sql_login=my_sql_login)#ettoday_crawler() 會回傳上一次爬到的url
    
    print('-----------CRAWLER IS SLEEPING-----------')
    time.sleep(7200)

