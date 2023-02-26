import os
import smtplib
from email.message import EmailMessage
from datetime import datetime
import shutil



username = os.environ['official_email_username']
password = os.environ['official_mail_password']

def send_unpaid_mail(df,user_email:dict):
  do_not_have_email = []
  today_year = f"{datetime.now().year}"
  today_month = f"{datetime.now().month:02.0f}"
  today_day = f"{datetime.now().day:02.0f}"
  os.mkdir("temp")

  with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
    server.login(username, password)
    for name, mail in user_email.items():
      name = name[0].upper()+name[1:]   
      if not mail:
        do_not_have_email.append(name)
      else:
        msg = EmailMessage()
        msg['From'] = username # 寄件人
        msg['To'] = mail # 收件人
        msg['Subject'] = f'{name}未付款帳單__催款通知{today_year}.{today_month}.{today_day}' # 標題

        ## 純文字內容
        text = f'Hi {name},\n以下是您欠款的金額，請抽空盡速繳納\n'        
        temp = df.loc[df['name']==name.lower()].copy()
        sum = temp['price'].sum()
        text += f'總計 {sum} 元\n詳細未付款明細，請見附件。\n'
        msg.set_content(text)
        file_name = f'{name}未付款明細_{today_year}{today_month}{today_day}.xlsx'

        # change the column title
        temp.rename(columns = {'u_date':'日期','name':'姓名','content':'餐點','price':'價格','buyer':'預付者','paid':'是否繳費'}, inplace = True)
        temp.reset_index(drop=True, inplace=True)
        temp.index += 1
        temp.to_excel('temp/'+file_name,index=1)  
        with open('temp/'+file_name,'rb') as f:
            file_data = f.read()
        msg.add_attachment(file_data, maintype="application", subtype="xlsx", filename=file_name)
        server.send_message(msg)
  shutil.rmtree("temp")
  return do_not_have_email
        
      