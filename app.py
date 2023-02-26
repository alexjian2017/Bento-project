from flask import Flask, render_template, request,jsonify
from database import sheet_to_user_db, email_to_db, update_paid_to_db, search_payment_from_db, search_unpaid_from_db
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
  t1 = time.time()
  data= request.form
  sheet_id = data['google_sheet_url'].split('/')[5]
  sheet_name = data['google_sheet_name']
  if len(sheet_id)!=44:
    return "請確認你輸入google_sheet網址的正確性",404  
  url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}' 

  try:
    df = pd.read_csv(url)
  except pd.errors.ParserError:
    return "請打開google表單權限",404
  if sheet_to_user_db(df,data['date'],data['buyer'].strip().lower()):
    t2 = time.time()
    print(f"工耗時:{t2-t1}")
    return "成功輸入資料"
  return '',404
  

@app.route("/user/set_email", methods=["GET","POST"])
def set_email():
  if request.method == 'POST':
    data= request.form
    result = email_to_db(data['name'].strip().lower(),data['email'].strip())
    if result == 1:
      return "添加成功"
    elif result == 2:
      return "修改成功"
    return 'Oops, something go wrong'
    
  return render_template('set_email.html')
   
  
@app.route("/user/paid", methods=["GET","POST"])
def paid():
  dic = {}
  if request.method == 'POST':
    data= request.form
    dic['name']=data['name']
    dic['buyer']=data['buyer']
    if "search" in data:
      result = search_payment_from_db(data['name'].strip(),data['buyer'].strip())
      search_price = result['sum(price)']
      if search_price:        
        dic['search_price'] = int(search_price)
      else:
        dic['search_price'] = 0
    else:
      if update_paid_to_db(data['name'],data['buyer']):
        return "繳費成功"
      return 'Oops, something go wrong' 
  return render_template('paid.html',dic=dic)

@app.route("/user/unpaid_email")
def unpaid_email():
  t1=time.time()
  do_not_have_email = search_unpaid_from_db('tisa')
  text = ", ".join(do_not_have_email)+"並沒有設定email，麻煩設定後再寄一次"
  t2=time.time()
  print(f"總共{t2-t1}秒")
  return text

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug = True)