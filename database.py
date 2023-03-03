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

def sheet_to_user_db(df):  
  
  # df['buyer']=buyer.strip().lower()
  # df['u_date']=date
  # Dtype ={'u_date':DATE,'name':VARCHAR(200),'content':VARCHAR(1000),'price':INT,'buyer':VARCHAR(200),'paid':BOOLEAN}

  try:
    with engine.connect() as conn: 
      for i in range(len(df.index)):
        paid = 1 if df.iloc[i,3] else 0
        conn.execute(text(f"insert into user_data(name,content,price,paid,buyer,u_date) values('{df.iloc[i,0]}','{df.iloc[i,1]}','{df.iloc[i,2]}','{paid}','{df.iloc[i,4]}','{df.iloc[i,5]}');"))
      # df.to_sql('user_data',conn,if_exists='append',index=False,chunksize=1000,dtype = Dtype)
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
      return 0
def search_unpaid_from_db(buyer:str):
  with engine.connect() as conn:
    query= f"select u_date,name,content,price,buyer,paid from user_data where buyer='{buyer}' and paid ='0' order by name, u_date;"
    #df = pd.read_sql(text(query), conn)
    rows = []
    result = conn.execute(text(query))
    for row in result:
      rows.append(row._asdict())
    df = pd.DataFrame(rows)
  return df
def search_from_db(name:str,buyer:str,start_date:str,end_date:str,paid:str):
  with engine.connect() as conn:
    query= f"select u_date,name,content,price,buyer,paid from user_data where buyer='{buyer}' "
    query += f"and paid='{1 if paid=='y' else 0}'" if paid in "yn" else "" 
    query += f"and name='{name}'" if name else ""
    query += f"and u_date>='{start_date}'" if start_date else ""
    query += f"and u_date<='{end_date}'" if end_date else ""
    query +=" order by u_date,name;"
    rows = []
    result = conn.execute(text(query))
    for row in result:
      rows.append(row._asdict())
    df = pd.DataFrame(rows)
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
  return user_email
  

  