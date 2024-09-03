import os
import requests
import urllib.parse

from flask import redirect, render_template, request, session
from functools import wraps

import csv
from datetime import datetime, timedelta
import pytz
import uuid

def usd(value):
    """Format value as USD."""
    return f"${value:,.2f}"

def lookup(symbol):
    """Look up quote for symbol."""
    symbol = symbol.upper()
    end = datetime.now(pytz.timezone("US/Eastern"))
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
        response = requests.get(url, cookies={"session": str(uuid.uuid4())}, headers={"User-Agent": "curl/7.68.0", "Accept": "*/*"})
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
    # except (requests.RequestException, ValueError, KeyError, IndexError):
    except Exception as e:
        print(e)
        return None

def usd(value):
    """Format value as USD."""
    return f"${value:,.2f}"

def get_news(query, days=7, count=4):
    """Get news articles based on query."""

    # Make News API request
    try:
        api_key = os.getenv("NEWS_API_KEY")
        date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        url = f"https://newsapi.org/v2/everything?q={urllib.parse.quote_plus(query)}&from={date}&sortBy=popularity&apiKey={api_key}"
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException:
        return None

    # Parse response
    try:
        response1 = response.json()
        response2 = response1["articles"]
        response3 = response2[:count] # Slice fisrt N elements of list 
        articles = []
        for item in response3:
            # News API gives date and time: 2021-06-12T00:05:00Z
            date = item["publishedAt"].replace("T", " ").replace("Z", "")

            article = {
                "source": item["source"]["name"],
                "title": item["title"],
                "description": item["description"],
                "url": item["url"],
                "url_to_image": item["urlToImage"],
                "date": datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
            }          
            articles.append(article)

        return articles
    except (KeyError, TypeError, ValueError):
        return None