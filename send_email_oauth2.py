import base64
import os
import pickle
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

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

# Usage
#send_email('samuel.pappas@outlook.com', 'Automated Email with Python', 'LETS GOOOOOOOO')

URL = 'https://www.academy.com/p/new-balance-mens-608-v5-performance-training-shoes?sku=white-10-5-eeee'


headers = {"User-Agent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'}

def check_price(): 
    page = requests.get(URL, headers=headers)
    # if page.status_code == 200:
    #     print("Request successful")
    # else:
    #     print(f"Request failed with status code {page.status_code}")


    soup = BeautifulSoup(page.content, 'html.parser')
    #print(soup.prettify()[:1000])  # Print first 1000 characters of the HTML to inspect

    title = soup.find(id="title")
    print(title)
    #print(title.get_text().strip() if title else "Title not found")

    price = soup.find_all("div", {"class": "promo"})
    #print(price)
    now_price = 10000
    for div in price:
        if div.get('data-auid') == 'nowPrice':
            now_price = div.get_text(strip=True)
            break
    if isinstance(now_price, str):
        now_price = float(now_price[1::])
    #elif isinstance(now_price, int):
    #    now_price = str(now_price)
    #    now_price = float(now_price[1::])
    else:
        print("not sure what type now_price is - You might need to verify the link as a human")
    print("Price: " + str(now_price))
    if now_price < 50:
        message = 'The price of your preferred item has dropped to: ' + str(now_price) + ' - Check it out here: ' + URL
        send_email('sbpappas0@gmail.com', 'Check this: Price has dropped', message)

check_price()