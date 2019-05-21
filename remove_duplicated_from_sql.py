import pandas as pd
import MySQLdb
from sqlalchemy import create_engine
   

#%% appledaily
def rm_dup_sql(table_name):
    my_sql_login = 'mysql+mysqldb://AmoLiu:news_317@140.112.153.64:3306/news?charset=utf8'

    engine = create_engine(my_sql_login, encoding='utf-8')
    connection = engine.connect()
    
    query_select = 'SELECT * FROM '+ table_name
    result_proxy = connection.execute(query_select)
    results = result_proxy.fetchall()
    df = pd.DataFrame(results, columns=results[0].keys())
    
    df_undplicated = df.drop_duplicates(subset='url')

    query_drop = 'DROP TABLE ' +  table_name
    connection.execute(query_drop)
    
    df_undplicated.to_sql(name=table_name, con=connection, if_exists='replace', index = False)
    print('Complete removing duplicated')            

#rm_dup_sql('chinatimes_realtime')
