import os
import requests
import urllib.parse

from flask import redirect, render_template, request, session
from functools import wraps

import csv
from datetime import datetime, timedelta
import pytz
import uuid


def lookup(symbol):
    """Look up quote for symbol."""
    symbol = symbol.upper()
    end = datetime.now(pytz.timezone("Asia/Singapore"))
    start = end - timedelta(days=7)

    # Yahoo Finance API
    url = (
        f"https://query1.finance.yahoo.com/v7/finance/download/{urllib.parse.quote_plus(symbol)}"
        f"?period1={int(start.timestamp())}"
        f"&period2={int(end.timestamp())}"
        f"&interval=1d&events=history&includeAdjustedClose=true"
    )

    # Query API
    try:
        response = requests.get(url, cookies={"session": str(uuid.uuid4())}, headers={"User-Agent": "python-requests", "Accept": "*/*"})
        response.raise_for_status()
        quotes = list(csv.DictReader(response.content.decode("utf-8").splitlines()))
        quotes.reverse()
        
        oldPr = float(quotes[1]["Adj Close"])
        closePr = float(quotes[0]["Adj Close"])
        
        price = round(closePr, 2)
        change = round(closePr - oldPr, 2)
        change_percent = round(((closePr - oldPr) / oldPr) * 100, 2)
        
        return {
            "name": symbol,
            "price": price,
            "symbol": symbol,
            "change": change,
            "change_percent": change_percent
        }
    except (requests.RequestException, ValueError, KeyError, IndexError):
        return None

def usd(value):
    """Format value as USD."""
    return f"${value:,.2f}"