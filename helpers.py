import csv
import datetime
import pytz
import requests
import subprocess
import urllib
import uuid

from flask import redirect, render_template, session
from functools import wraps


def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


import requests

def lookup(symbol):
    """Lookup stock quote."""

    # Define the API URL
    url = f"https://cloud.iexapis.com/stable/stock/{symbol}/quote/?token=YOUR_API_KEY"

    # Make the API request
    response = requests.get(url)

    # If the request was successful
    if response.status_code == 200:
        data = response.json()

        return {
            "symbol": data.get("symbol"),
            "name": data.get("companyName"),
            "price": data.get("latestPrice")
        }
    else:
        return None



def usd(value):
    """Format value as USD."""
    return f"${value:,.2f}"
