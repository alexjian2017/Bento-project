import os
from sqlalchemy import create_engine, text
import pymysql

db_connection_str = os.environ['db_connection_str']
engine = create_engine(
  db_connection_str,
  connect_args={
    "ssl": {
      "ssl_ca": "/etc/ssl/cert.pem"
    }
  })

def google_to_user_db(df,date:str,buyer:str):  
  try:
    with engine.connect() as conn: 
      for i in range(len(df.index)):
        if isinstance(df.iloc[i,0],str):
          name = df.iloc[i,0].lower()
          content = df.iloc[i,1]
          price = df.iloc[i,2]
          paid = 1 if df.iloc[i,3] else 0
          query = f"insert into user_data (u_date,name,price,content,buyer,paid) values('{date}','{name}','{price}','{content}','{buyer}','{paid}')"
          conn.execute(text(query))
    return 1
  except pymysql.MySQLError as err:
    print(type(err), err)
  return 0
