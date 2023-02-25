from flask import Flask, render_template, request
from database import google_to_user_db
import pandas as pd
import time

app = Flask(__name__)

@app.route("/")
def home():
  return render_template('home.html')

@app.route("/test", methods=["POST"])
def user_enter_google_sheet():
  t1 = time.time()
  data= request.form
  sheet_id = data['google_sheet_url'].split('/')[5]
  sheet_name = data['google_sheet_name']
  if len(sheet_id)!=44:
    return "請確認你輸入google_sheet網址的正確性",404  
  url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}' 
  print(sheet_id,sheet_name)

  try:
    df = pd.read_csv(url)
  except pd.errors.ParserError:
    return "請打開google表單權限",404
  if google_to_user_db(df,data['date'],data['buyer'].lower()):
    t2 = time.time()
    print(f"工耗時:{t2-t1}")
    return "成功輸入資料"
  return '',404

  
if __name__ == '__main__':
    app.run(host='0.0.0.0',debug = True)