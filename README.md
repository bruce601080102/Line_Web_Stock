## 安裝
```python
! pip install twstock
! pip install hanziconv
! pip install gtts
```
## 步驟
1.網址申請:https://developers.line.biz/en/

2.解壓縮 ngrok.rar
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 開啟anconda對應的環境及資料夾位置，輸入` ngrok http 5000`
#####&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Messaging API>Webhook settings:
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 輸入Forwarding中的網址+/callback
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; `如 https://f762366f5278.ngrok.io/callback`
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 打開Use webhook

3.在line Developers 需要兩組密碼
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 在Basic settings>Channel secret 中有一組密碼
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Messaging API>Channel access token中有一組密碼
```python

#Channel access token
line_bot_api = LineBotApi('UBq1eOQ8JnHzYTjQNCva4z48XI/WxYy16T9okVyWJ2R3To1MgP4EVKTabHCE6PmznJlwCFFs3/cRzq2vHCFzrhSfx/0/Wu129SKe1AMrnlhnKgNmkfNYu8uMxM/J190FDtTQwfp3iRA0u+liYpKW6QdB04t89/1O/w1cDnyilFU=') 

#Channel secret 
handler = WebhookHandler('410b098a32f3632c01908750c161c231') 
```
4.加入自己所創的官方line帳號輸入股票名稱即可
