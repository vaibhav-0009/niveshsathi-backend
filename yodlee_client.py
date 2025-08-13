# ✅ yodlee_client.py
import requests
import os
from dotenv import load_dotenv

load_dotenv()
YODLEE_API_BASE = "https://sandbox.api.yodlee.com/ysl"
YODLEE_CLIENT_ID = os.getenv("YODLEE_CLIENT_ID")
YODLEE_SECRET = os.getenv("YODLEE_SECRET")

# 🔐 App token

def get_access_token():
    url = f"{YODLEE_API_BASE}/auth/token"
    headers = {
        "Api-Version": "1.1",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = f"clientId={YODLEE_CLIENT_ID}&secret={YODLEE_SECRET}&grant_type=client_credentials"
    response = requests.post(url, headers=headers, data=data)
    return response.json().get("access_token")

# 👤 Login user (by username)

def login_user(app_token, username):
    url = f"{YODLEE_API_BASE}/user/login"
    headers = {
        "Api-Version": "1.1",
        "Authorization": f"Bearer {app_token}",
        "Content-Type": "application/json"
    }
    data = {"user": {"loginName": username, "appId": "10003600"}}
    response = requests.post(url, headers=headers, json=data)
    return username if response.status_code in [200, 201] else None

# 📄 Transactions

def fetch_transactions(app_token, user_token, from_date, to_date):
    url = f"{YODLEE_API_BASE}/transactions?fromDate={from_date}&toDate={to_date}"
    headers = {
        "Api-Version": "1.1",
        "Authorization": f"Bearer {app_token}",
        "loginName": user_token
    }
    return requests.get(url, headers=headers).json()

# 📊 Holdings

def fetch_holdings(app_token, user_token):
    url = f"{YODLEE_API_BASE}/holdings"
    headers = {
        "Api-Version": "1.1",
        "Authorization": f"Bearer {app_token}",
        "loginName": user_token
    }
    return requests.get(url, headers=headers).json()

# 🧠 Net worth

def fetch_networth(app_token, user_token):
    url = f"{YODLEE_API_BASE}/derived/networth"
    headers = {
        "Api-Version": "1.1",
        "Authorization": f"Bearer {app_token}",
        "loginName": user_token
    }
    return requests.get(url, headers=headers).json()
