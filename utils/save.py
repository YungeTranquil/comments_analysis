import pandas as pd
from sqlalchemy import create_engine

def dataframe_to_mysql(df, table_name, database_url):

    database_url = "mysql+pymysql://root:a1258896@1.tcp.cpolar.cn:24150/spider"
    table_name = 'google_search'
    # 创建数据库引擎
    engine = create_engine(database_url)
    
    # 使用to_sql方法上传DataFrame
    df.to_sql(table_name, con=engine, if_exists='append', index=False)
    
    # print(f"DataFrame uploaded to `{table_name}` table in the database.")