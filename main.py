import os
import requests
import datetime
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()

STOCK = "TSLA"
COMPANY_NAME = "Tesla"

TODAY = datetime.date.today()
YESTERDAY = TODAY - datetime.timedelta(days=1)
EREYESTERDAY = TODAY - datetime.timedelta(days=2)

ALPHA_API_KEY = os.getenv("ALPHA_API_KEY")
ALPHA_URL = "https://www.alphavantage.co/query"
ALPHA_PARAMS = {
    'apikey': ALPHA_API_KEY,
    'symbol': STOCK,
    'function': 'TIME_SERIES_DAILY_ADJUSTED',
}

response = requests.get(ALPHA_URL, ALPHA_PARAMS)
response.raise_for_status()
data = response.json()['Time Series (Daily)']

yesterday_close = float(data[str(YESTERDAY)]['4. close'])
ereyesterday_close = float(data[str(EREYESTERDAY)]['4. close'])
price_shift = 100 * (yesterday_close - ereyesterday_close)/ereyesterday_close


NEWS_API_KEY = os.getenv("NEWS_API_KEY")
NEWS_URL = "https://newsapi.org/v2/everything"
NEWS_PARAMS = {
    'apiKey': NEWS_API_KEY,
    'q': COMPANY_NAME,
    'from': YESTERDAY
}

news_response = requests.get(NEWS_URL, NEWS_PARAMS)
stories = news_response.json()['articles'][:3]

TWILIO_ACC_SID = os.getenv("TWILIO_ACC_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_MOBILE = os.getenv("TWILIO_MOBILE")

MY_MOBILE_NUMBER = os.getenv("MY_MOBILE_NUMBER")

if price_shift < 0:
    price_change_str = f"🔻{round(-price_shift)}%"
else:
    price_change_str = f"🔺{round(price_shift)}%"

STOCK_UPDATE_TEXT = f"""
 
TSLA: {price_change_str}
{stories[0]['title']}\n 
{stories[1]['title']}\n
{stories[2]['title']}
"""


def send_text_update():
    account_sid = TWILIO_ACC_SID
    auth_token = TWILIO_AUTH_TOKEN
    client = Client(account_sid, auth_token)

    message = client.messages.create(
        body=STOCK_UPDATE_TEXT,
        from_=TWILIO_MOBILE,
        to=MY_MOBILE_NUMBER
    )
    print(message.status)


if abs(price_shift) > 3:
    send_text_update()
else:
    print(price_change_str)
