import os
from sqlalchemy import create_engine, text
from sqlalchemy.types import DATE,VARCHAR,INT,BOOLEAN
import pymysql
import pandas as pd

db_connection_str = os.environ['db_connection_str']
engine = create_engine(
  db_connection_str,
  connect_args={
    "ssl": {
      "ssl_ca": "/etc/ssl/cert.pem"
    }
  })

def sheet_to_user_db(df,date:str,buyer:str):  
  
  df['buyer']=buyer.strip().lower()
  df['u_date']=date
  Dtype ={'u_date':DATE,'name':VARCHAR(200),'content':VARCHAR(1000),'price':INT,'buyer':VARCHAR(200),'paid':BOOLEAN}

  try:
    with engine.connect() as conn: 
      df.to_sql('user_data',conn,if_exists='append',index=False,chunksize=1000,dtype = Dtype)
    return 1
  except pymysql.MySQLError as err:
    print(type(err), err)
  return 0

def email_to_db(name:str,email:str):
  with engine.connect() as conn:
    try:
      conn.execute(text(f"insert into user_email(name,email) values('{name}','{email}');"))
      return 1
    except:  
      conn.execute(text(f"update user_email set email='{email}' where name='{name}';"))
      return 2
    return 0

def update_paid_to_db(name:str,buyer:str):
  with engine.connect() as conn:
    try:
      conn.execute(text(f"update user_data set paid='1' where name='{name}' and buyer='{buyer}';"))
      return 1
    except:  
      return 0

def search_payment_from_db(name:str,buyer:str):
  with engine.connect() as conn:
    try:
      query = f"select sum(price) from user_data where name='{name}' and buyer='{buyer}' and paid ='0';"
      result = conn.execute(text(query))
      
      if not result:
        return None
      for row in result:
        return row._asdict()
      
      return 1
    except:
      print('error')
      return 0
def search_unpaid_from_db(buyer:str):
  with engine.connect() as conn:
    query= f"select u_date,name,content,price,buyer,paid from user_data where buyer='{buyer}' and paid ='0' order by name, u_date;"
    df = pd.read_sql(text(query), conn)
    
  return df
def search_email_from_db(names):
  user_email = {}
  with engine.connect() as conn:
    for name in names:
      query = f"select email from user_email where name='{name}'"
        
      result = conn.execute(text(query))
      for row in result:
        rowdata = row._asdict()
        user_email[name] = rowdata['email']
      if name not in user_email:
        user_email[name] = None
  print('user_email:',user_email)
  return user_email
  

  