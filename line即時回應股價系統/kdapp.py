import warnings
warnings.filterwarnings("ignore")
import twstock
import talib
import numpy as np
import pandas as pd
import pandas_datareader as pdr
import matplotlib.pyplot as plt
import seaborn as sns
import datetime as datetime
# machine learning
from sklearn.svm import SVC, LinearSVC
from sklearn.model_selection import train_test_split
from sklearn import preprocessing
from sklearn.model_selection import cross_val_score
from sklearn.metrics import confusion_matrix
from sklearn.metrics import classification_report
from sklearn.svm import SVR
import twstock
import re
import os
from bs4 import BeautifulSoup
import requests
from hanziconv import HanziConv

from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)
import twstock

import re
import os
from bs4 import BeautifulSoup
import requests
from hanziconv import HanziConv

def data_Engineering_k(name,year=2017,month=12,day=20):
    k=[]
    d=[]
    
    start = datetime.datetime(year,month,day)
    df_2330 = pdr.DataReader(str(name)+'.TW', 'yahoo', start=start)
    sma_10 = talib.SMA(np.array(df_2330['Close']), 10)
    sma_30 = talib.SMA(np.array(df_2330['Close']), 30)
    df_2330['k'], df_2330['d'] = talib.STOCH(df_2330['High'], df_2330['Low'], df_2330['Close'])
    df_2330['k'].fillna(value=0, inplace=True)
    df_2330['d'].fillna(value=0, inplace=True) 
    data=df_2330[8:]
    
    for i in range(len(data['k'])-1):
        k.append(data['k'][i]-data['k'][i+1])

    for i in range(len(data['d'])-1):
        d.append(data['d'][i]-data['d'][i+1])   
    dict_k ={'result_k':k} 
    dict_d ={'result_d':d}   
    data_k=pd.DataFrame(dict_k)
    data_d=pd.DataFrame(dict_d)
    data_index=data.reset_index(drop=True)
    concat_pd=pd.concat([data_index,data_k,data_d],axis=1)
    concat_pd['result_k']=concat_pd['result_k']>=0
    concat_pd['result_d']=concat_pd['result_d']>=0
    data_main=concat_pd.replace(True,1)
    
    
    train=data_main[['High', 'Low', 'Open', 'Close','k','d']]
    X = preprocessing.scale(train)
    X=pd.DataFrame(X,columns=['High', 'Low', 'Open', 'Close','k','d'])
    X_pre=X[-1:]
    Y_k = data_main['result_k']
    Y_d = data_main['result_d']
    
    return X_pre,X,Y_d,Y_k

#-----------------------------------------------------------------
def get_price(stockid):   # 取得股票名稱和及時股價
    rt = twstock.realtime.get(stockid)   # 取得台積電的及時交易資訊
    if rt['success']:                    # 如果讀取成功
        a=float(rt['realtime']['best_bid_price'][0])
        b=float(rt['realtime']['best_bid_price'][1])
        c=float(rt['realtime']['best_bid_price'][2])
        d=float(rt['realtime']['best_bid_price'][3])
        return (rt['info']['name'],      #←傳回 (股票名稱, 及時價格)
               float( rt['realtime']['latest_trade_price']))
    else:
        return (False, False)

def get_best(stockid):     # 檢查是否符合四大買賣點
    stock = twstock.Stock(stockid)
    bp = twstock.BestFourPoint(stock).best_four_point()
    if(bp):
        return ('買進' if bp[0] else '賣出', bp[1])  #←傳回買進或賣出的建議
    else:
        return (False, False)  #←都不符合

def bot_get_wiki(keyword):
    response = requests.get('https://zh.wikipedia.org/zh-tw/' + keyword)
    bs = BeautifulSoup(response.text, 'lxml')
    p_list = bs.find_all('p')
    for p in p_list:
        if keyword in p.text[0:10]:
            return p.text

# 唸出常規表達式處理後的字串

def bot_speak_re(sentence):
    s1 = re.sub(r'\[[^\]]*\]', '', sentence)

    return s1

# 對 Google 搜尋結果進行網路爬蟲


def bot_get_google(question):
    url = 'https://www.google.com.tw/search?q={' + question + '}+股票'
    #print(url)
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
                             ' AppleWebKit/537.36 (KHTML, like Gecko)'
                             ' Chrome/70.0.3538.102 Safari/537.36'}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        bs = BeautifulSoup(response.text, 'lxml')
        wiki_url = bs.find('h3')
        # kwd = wiki_url.text.split('/')[-1]
        kwd = wiki_url.text.split('›')[-1].replace(' ','')      # 修正
        #keyword_trad = HanziConv.toTraditional(kwd)
        return kwd
    else:
        print('請求失敗')

app = Flask(__name__)

line_bot_api = LineBotApi('UBq1eOQ8JnHzYTjQNCva4z48XI/WxYy16T9okVyWJ2R3To1MgP4EVKTabHCE6PmznJlwCFFs3/cRzq2vHCFzrhSfx/0/Wu129SKe1AMrnlhnKgNmkfNYu8uMxM/J190FDtTQwfp3iRA0u+liYpKW6QdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('410b098a32f3632c01908750c161c231')


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):

    all_dict=twstock.codes
    dict_name_code={}
    for i in list(all_dict.keys()):
        name = all_dict[i][2]
        dict_name_code[name]=i    

    search = bot_get_google(event.message.text)
    time=0
    for i in search:
        if i=='(':
            break
        time+=1
    key=search[0:time]
    print(key)
    name, price = get_price(dict_name_code[key])  
    act, why = get_best(dict_name_code[key]) 
    try:
        #訓練-------
        X_pre,X,Y_d,Y_k = data_Engineering_k(int(dict_name_code[key]))
        X_train_d,X_test_d,y_train_d,y_test_d = train_test_split(X[:-1],Y_d[:-1],test_size=0.2)
        X_train_k,X_test_k,y_train_k,y_test_k = train_test_split(X[:-1],Y_k[:-1],test_size=0.2)
        # SVM---
        svc_D  = SVC(C=100,probability=True)
        svc_D = svc_D.fit(X_train_d, y_train_d)
        # SVM---
        svc_K  = SVC(C=100,probability=True)
        svc_K = svc_K.fit(X_train_k, y_train_k)
        #預測kd線-----
        pre_d=svc_D.predict(X_pre)
        pre_k=svc_K.predict(X_pre)
        print('pre_d',pre_d,'pre_k',pre_k)
        if pre_d ==1 and pre_k==1:
            pre='明天預測 kd線都下降'
        if pre_d ==0 and pre_k==0:
            pre='明天預測 kd線都上升'
        if pre_d ==1 and pre_k==0:
            pre='明天預測 k線上升，d線下降，可能回穩'
        if pre_d ==0 and pre_k==1:
            pre='明天預測 k線下降，d線上升，需要警慎'





        repeat='公司名稱:'+name+' '*45+'最後交易:'+str(price)+' '*45+'建議:'+act+' '*55+why+' '*20+'機器預測:'+pre
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=repeat)
        )
        print(repeat)
    except:
        search = bot_get_google(event.message.text)
        time=0
        for i in search:
            if i=='(':
                break
            time+=1
        key=search[0:time]
        print(key)
        name, price = get_price(dict_name_code[key])  
        act, why = get_best(dict_name_code[key])     
        repeat='公司名稱:'+name+'-----'+'最後交易:'+str(price)+'-----'+'建議:'+act+'-----'+why+'，查無歷史資料無法預測kd線'
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=repeat)
        )


        print(repeat)

        
        
        
if __name__ == "__main__":
    app.run()
