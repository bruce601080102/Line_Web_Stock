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
#from gtts import gTTS
import os
from bs4 import BeautifulSoup
import requests
from hanziconv import HanziConv
import twstock

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
        
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    
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
    repeat='公司名稱:'+name+'-----'+'最後交易:'+str(price)+'-----'+'建議:'+act+'-----'+why
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=repeat)
    )

    
    print(repeat)

if __name__ == "__main__":
    all_dict=twstock.codes
    dict_name_code={}
    for i in list(all_dict.keys()):
        name = all_dict[i][2]
        dict_name_code[name]=i
    app.run()