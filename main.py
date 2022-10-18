import requests
from twilio.rest import Client
import os
from dotenv import load_dotenv

load_dotenv()

STOCK_NAME = "TSLA"
COMPANY_NAME = "Tesla Inc"

STOCK_ENDPOINT = os.getenv("STOCK_ENDPOINT")
NEWS_ENDPOINT = os.getenv("NEWS_ENDPOINT")

STOCK_API_KEY = os.getenv("STOCK_API_KEY")
stock_parameters = {
    "function": "TIME_SERIES_DAILY",
    "symbol": STOCK_NAME,
    "apikey": STOCK_API_KEY,
}

NEWS_API_KEY = os.getenv("NEWS_API_KEY")
news_parameters = {
    "q": COMPANY_NAME,
    "apiKey": NEWS_API_KEY,
    "sortBy": "relevancy",
}

ACCOUNT_SID = os.getenv("ACCOUNT_SID")
AUTH_TOKEN = os.getenv("AUTH_TOKEN")

TO_PHONE_NUMBER = os.getenv("TO_PHONE_NUMBER")
FROM_PHONE_NUMBER = os.getenv("FROM_PHONE_NUMBER")

stock_response = requests.get(STOCK_ENDPOINT, params=stock_parameters)
stock_response.raise_for_status()
stock_data = stock_response.json()["Time Series (Daily)"]
data_list = [value for (key,value) in stock_data.items()]
yesterday_data = data_list[0]
yesterday_closing_price = float(yesterday_data["4. close"])

two_days_ago_data = data_list[1]
two_days_ago_closing_price = float(two_days_ago_data["4. close"])

difference = yesterday_closing_price - two_days_ago_closing_price

up_down = None

if difference > 0:
    up_down = "🔺"
else:
    up_down = "🔻"

percentage_difference = abs(round((difference / yesterday_closing_price) * 100))

if percentage_difference > 1:
    news_response = requests.get(NEWS_ENDPOINT, params=news_parameters)
    news_response.raise_for_status()
    news_data = news_response.json()["articles"]
    top_3_articles = news_data[:3]

    formatted_articles = [f"{STOCK_NAME}: {up_down}{percentage_difference}% \nHeadline: {article['title']} \nBrief: {article['description']}" for article in top_3_articles]

    client = Client(ACCOUNT_SID, AUTH_TOKEN)

    for article in formatted_articles:
        message = client.messages \
                .create(
                    body=article, 
                    from_=FROM_PHONE_NUMBER,
                    to=TO_PHONE_NUMBER,
                )
        print(message.status)

