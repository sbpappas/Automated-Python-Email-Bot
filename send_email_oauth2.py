import base64
import os
import pickle
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import time

#for web scraper:import requests
from bs4 import BeautifulSoup
import smtplib
import requests

# Update SCOPES to include gmail.readonly
SCOPES = [
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.readonly'
]
TOKEN_PICKLE_PATH = 'token.pickle'
CREDENTIALS_PATH = 'credentials.json'

def get_authenticated_email(creds):
    service = build('gmail', 'v1', credentials=creds)
    user_info = service.users().getProfile(userId='me').execute()
    return user_info['emailAddress']

def send_email(to_email, subject, message):
    creds = None
    if os.path.exists(TOKEN_PICKLE_PATH):
        with open(TOKEN_PICKLE_PATH, 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_PICKLE_PATH, 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)

    from_email = get_authenticated_email(creds)

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(message, 'plain'))

    raw = base64.urlsafe_b64encode(msg.as_string().encode('utf-8')).decode('utf-8')
    body = {'raw': raw}

    try:
        message = service.users().messages().send(userId='me', body=body).execute()
        print(f'Message Id: {message["id"]}')
    except Exception as e:
        print(f'An error occurred: {e}')

#URL = 'https://www.academy.com/p/new-balance-mens-608-v5-performance-training-shoes?sku=white-10-5-eeee'
#URL = 'https://shop.atlasskateboarding.com/collections/footwear/products/nike-air-max-ishod-1'
URL = 'https://shop.atlasskateboarding.com/collections/sale/products/converse-as-1-pro-ox-3'

headers = {"User-Agent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'}

def check_price(): 
    page = requests.get(URL, headers=headers)
    # if page.status_code == 200:
    #     print("Request successful")
    # else:
    #     print(f"Request failed with status code {page.status_code}")


    soup = BeautifulSoup(page.content, 'html.parser')
    #print(soup.prettify()[:1000])  # Print first 1000 characters of the HTML to inspect

    title = soup.find("div", class_="product-title")

    if title:
        title = title.get_text().strip()
        print(title)
    else: print("Title not found")

    #price = soup.find_all("div", {"class": "promo"}) # for academy shoes
    price = soup.find("span", class_="sale-price")
    if not price:
        price = soup.find("div", class_="product-price") # for atlas 
    now_price = 10000
    if price:
        now_price = price.get_text(strip=True)
        print(f"The price is: {now_price}")
    else:
        print("Price div not found.")
    # for div in price:
    #     if div.get('data-auid') == 'nowPrice':
    #         now_price = div.get_text(strip=True)
    #         print("got the price")
    #         break
    # if isinstance(now_price, str):
    #     now_price = float(now_price[1::])
    #     print("Price: " + str(now_price))
    # else:
    #     print("not sure what type now_price is - You might need to verify the link as a human")
    now_price = float(now_price[1::])
    if now_price < 112:
        message = 'The price of your preferred item - ' + str(title) + ' - has dropped to: $' + str(now_price) + ' - Check it out here: ' + URL
        send_email('sbpappas0@gmail.com', 'PRICE DROP: ' + str(title), message)

check_price()

# while(True):
#     check_price()
#     time.sleep(60 * 60 * 24)