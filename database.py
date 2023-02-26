import os
from sqlalchemy import create_engine, text
import pymysql
import pandas as pd
from send_email import send_unpaid_mail

db_connection_str = os.environ['db_connection_str']
engine = create_engine(
  db_connection_str,
  connect_args={
    "ssl": {
      "ssl_ca": "/etc/ssl/cert.pem"
    }
  })

def sheet_to_user_db(df,date:str,buyer:str):  
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
      print(f"update user_data set paid='1' where name='{name} and 'buyer='{buyer}';")
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
      df = pd.read_sql_query(text(query), conn)
      
      user_email ={}
      for name in df['name'].unique():
        query1 = f"select email from user_email where name='{name}'"
        print(query1)
        
        result = conn.execute(text(query1))
        for row in result:
          a = row._asdict()
          user_email[name] = a['email']
        if name not in user_email:
          user_email[name] = None
      print('user_email:',user_email)

  return send_unpaid_mail(df,user_email)

  