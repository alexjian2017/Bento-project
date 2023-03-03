from flask import Flask, render_template, request, jsonify
from database import sheet_to_user_db, email_to_db, update_paid_to_db, search_email_from_db, search_from_db
from send_email import send_unpaid_mail, send_order_mail

import pandas as pd
import time

app = Flask(__name__)

@app.route("/")
def home():
  return render_template('home.html')
  
@app.route("/user/input")
def google_sheet():
  return render_template('google_sheet_form.html')
@app.route("/user/input/result", methods=["POST"])
def user_input_google_sheet():
  data= request.form
  content = {}
  sheet_id = data['google_sheet_url'].split('/')[5]
  sheet_name = data['google_sheet_name']
  if len(sheet_id)!=44:    
    content['error']= "請確認你輸入google_sheet網址的正確性" 
    return render_template('success.html',content=content)
  url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}' 
  try:
    df = pd.read_csv(url)
  except pd.errors.ParserError:
    content['error']= "請打開google表單權限"
    return render_template('success.html',content=content)
  df.rename(columns = {'姓名':'name','餐點':'content','價格':'price','繳費':'paid'}, inplace = True)
  df = df[df['name'].notna()&df['price'].notna()&df['paid'].notna()] 
  df = df[['name','content','price','paid']]  
  df['buyer']=data['buyer']
  df['date']=data['date']
  if sheet_to_user_db(df):
    content['success'] = "成功輸入資料"
    if 'need_email' in data:
      user_email = search_email_from_db(df['name'].unique())
      do_not_have_email = send_order_mail(df,data['date'],user_email)
      content['error'] = "但是 "+", ".join(do_not_have_email)+" 尚未設定email" 

    content['df'] = df
    content['rows'] =  [x for x in range(len(df.index))]
    content['columns'] =  [x for x in range(len(df.columns))]
  else:  
    content['error']= "GG，好像有甚麼東西發生錯誤了，請檢查輸入資料"
  return render_template('success.html',content=content)
  

@app.route("/user/set_email", methods=["GET","POST"])
def set_email():
  if request.method == 'POST':
    data= request.form
    content = {}
    df = pd.DataFrame(data.to_dict(flat=False))
    name = data['name'].strip().lower()
    email = data['email'].strip()
    result = email_to_db(name,email)
    content['df'] = df
    content['rows'] =  [x for x in range(len(df.index))]
    content['columns'] =  [x for x in range(len(df.columns))]
    if result == 1:
      content['success'] = "添加成功"
    elif result == 2:
      content['success'] = "修改成功"
    else:
      content['error']= "GG，好像有甚麼東西發生錯誤了，請檢查輸入資料"
    return render_template('success.html',content=content)
    
  return render_template('set_email.html')

@app.route("/user/search", methods=["GET","POST"])
def search():
  content = {}
  if request.method == 'POST':
    data= request.form
    content['name']=data['name']
    content['buyer']=data['buyer']
    content['start_date']=data['start_date']
    content['end_date']=data['end_date']
    content['paid']=data['paid']
    try:
      df = search_from_db(data['name'].strip(),data['buyer'].strip(),data['start_date'],data['end_date'],data['paid'].strip().lower())
    except Exception as err:
      content['error']= f"GG，好像有甚麼東西發生錯誤了\n{err}"
      return render_template('success.html',content=content)
    content['df'] = df
    content['rows'] =  [x for x in range(len(df.index))]
    content['columns'] =  [x for x in range(len(df.columns))]
  return render_template('search.html',content=content)
  
@app.route("/user/paid", methods=["GET","POST"])
def paid():
  content = {}
  if request.method == 'POST':
    data= request.form
    content['name']=data['name'].strip()
    content['buyer']=data['buyer'].strip()
    if "search" in data:
      try:
        df = search_from_db(content['name'],content['buyer'],None,None,'n')
      except Exception as err:
        content['error']= f"GG，好像有甚麼東西發生錯誤了\n{err}"
        return render_template('success.html',content=content)
      content['df'] = df
      content['rows'] =  [x for x in range(len(df.index))]
      content['columns'] =  [x for x in range(len(df.columns))]
      content['sum'] = df['price'].sum() if len(df.index) else 0
    else:
      if update_paid_to_db(content['name'],content['buyer']):
        content['error']= f"{content['name']} 繳費成功" 
      else:
        content['error']= "GG，好像有甚麼東西發生錯誤了"
      return render_template('success.html',content=content)
  return render_template('paid.html',content=content)

@app.route("/user/unpaid_email")
def unpaid_email():
  content = {}
  try:
    df = search_unpaid_from_db('tisa')
    user_email = search_email_from_db(df['name'].unique())
    do_not_have_email = send_unpaid_mail(df, user_email)
    content['error']= "寄送催繳通知成功"
    if do_not_have_email:    
      content['error'] += "，\n但是"+", ".join(do_not_have_email)+"尚未設定email"  
  except Exception as err:
      content['error']= f"GG，好像有甚麼東西發生錯誤了\n{err}"
  return render_template('success.html',content=content)

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug = True)