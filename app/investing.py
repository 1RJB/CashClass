import os
from flask import Flask, Blueprint, flash, redirect, render_template, request, session
from markupsafe import escape
from datetime import datetime
from .utils import lookup
from flask_login import (
    current_user,
    login_required,
)
from .models import Users, Holding, Transaction
from . import db

investing = Blueprint('investing', __name__)

@investing.route("/portfolio")
@login_required
def portfolio():
    """Show portfolio of user's stock holdings"""

    # Query database for current user's stock holdings (portfolio)
    user = current_user
    holdings = user.holdings
    stocks = [] # List of stock dicts
    transactions = user.transactions

    portfolio_cost = 0
    portfolio_value = 0

    # Get current prices for stocks using API
    for holding in holdings:
        quote = lookup(holding.symbol)
        stock = {}
        stock["symbol"] = holding.symbol
        stock["name"] = quote["name"]
        stock["price"] = float(quote["price"])
        stock["shares"] = int(holding.shares)
        stock["total_value"] = float(quote["price"]) * int(holding.shares)

        # Calculate cost of shares (total price paid)
        cost = 0
        for transaction in transactions:
            if transaction.symbol == stock["symbol"]:
                cost += transaction.shares * transaction.price # Sold shares will be negative

        stock["cost"] = cost / holding.shares
        stock["total_cost"] = cost
        stocks.append(stock) # Append stock dict to list of stocks
        portfolio_value += stock["total_value"]

    # Calculate cost of all portfolio transactions
    # Don't need to check for only single transaction since SQLAlchemy
    # with relationship returns InstrumentedList
    # If sold stock, will subtract since shares in transaction will be negative
    for transaction in transactions:
        portfolio_cost += transaction.shares * transaction.price

    # Format current user's portfolio info
    user_info = {
        "cash": user.cash,
        "portfolio_cost": portfolio_cost,
        "portfolio_value": portfolio_value,
        "gain_loss": portfolio_value - portfolio_cost
    }

    return render_template("portfolio.html", stocks=stocks, user_info=user_info)

@investing.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of a stock"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Validate length and alphabetical nature of symbol string
        if not (len(request.form.get("symbol")) <= 5 and request.form.get("symbol").isalpha()):
            return render_template("buy.html", error="Invalid symbol"), 400

        quote = lookup(request.form.get("symbol"))

        # Check if the symbol entry is valid
        if not quote:
            return render_template("buy.html", error="Invalid symbol"), 400

        # Check if shares entry is numeric
        elif not (request.form.get("shares")).isdigit():
            return render_template("buy.html", error="Invalid entry"), 400

        # Check if shares entry is an integer
        elif not float(request.form.get("shares")).is_integer():
            return render_template("buy.html", error="Invalid entry"), 400

        # Check if shares entry is non-negative
        elif int(request.form.get("shares")) <= 0:
            return render_template("buy.html", error="Share bought must be greater than zero"), 400

        # Check if user has enough money to complete purchase of shares
        user = current_user

        if quote["price"] * int(request.form.get("shares")) > user.cash:
            return render_template("buy.html", error="Not enough cash to complete purchase"), 400

        # Record transaction in database
        new_transaction = Transaction(
            user_id=user.email,
            symbol=quote["symbol"],
            shares=int(request.form.get("shares")),
            price=quote["price"],
            timestamp=datetime.now(),

        )
        db.session.add(new_transaction)

        # Deduct cash from user
        user.cash -= quote["price"] * int(request.form.get("shares"))

        # Update user's stock holdings (portfolio)
        # Check if stock is already in holdings
        found_holding = Holding.query.filter((Holding.user_id == user.email) & (Holding.symbol == new_transaction.symbol)).first()

        # Add stock to holdings if not already owned
        if found_holding == None:
            new_holding = Holding(
                user_id=user.email,
                symbol=new_transaction.symbol,
                shares=new_transaction.shares
            )
            db.session.add(new_holding)

        # Update stock in holdings if already owned
        else:
            found_holding.shares += new_transaction.shares

        # Save all changes to database
        db.session.commit()

        flash("Purchase completed")
        return redirect("/portfolio")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("buy.html")


@investing.route("/buy/<string:symbol>")
@login_required
def buy_symbol(symbol):
    return render_template("buy.html", symbol=escape(symbol))


@investing.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of a stock"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Validate length and alphabetical nature of symbol string
        if not (len(request.form.get("symbol")) <= 5 and request.form.get("symbol").isalpha()):
            return render_template("sell.html", error="Invalid symbol"), 400

        quote = lookup(request.form.get("symbol"))

        # Check if the symbol entry is valid
        if not quote:
            return render_template("sell.html", error="Invalid symbol"), 400

        # Check if shares entry is numeric
        elif not (request.form.get("shares")).isdigit():
            return render_template("sell.html", error="Invalid entry"), 400

        # Check if shares entry is an integer
        elif not float(request.form.get("shares")).is_integer():
            return render_template("sell.html", error="Invalid entry"), 400

        # Check if shares entry is non-negative
        elif int(request.form.get("shares")) < 0:
            return render_template("sell.html", error="share sold must be greater than zero"), 400

        # Query database to find stock in user's holdings
        user = current_user
        holding = Holding.query.filter((Holding.user_id==user.email) & (Holding.symbol==quote["symbol"])).first()

        # Check if user owns shares of stock user wants to sell
        if holding == None:
            return render_template("sell.html", error="You do not own shares in this company"), 400

        # Check if user owns enough shares user intends to sell
        elif holding.shares < int(request.form.get("shares")):
            return render_template("sell.html", error="You do not own that many shares to sell"), 400

        # Record transaction
        new_transaction = Transaction(
            user_id=user.email,
            symbol=quote["symbol"],
            shares=int(request.form.get("shares")) * (-1),
            price=quote["price"],
            timestamp=datetime.now()
        )
        db.session.add(new_transaction)

        # Add funds from sale to user's account
        user.cash += (int(request.form.get("shares")) * quote["price"])

        # If selling all stock, delete from holdings
        if holding.shares == new_transaction.shares:
            db.session.delete(holding)

        # Otherwise, update the holding for the stock in the database
        else:
            holding.shares += new_transaction.shares # += because shares is negative due to sale

        # Save all changes to database
        db.session.commit()

        flash("Sale completed")
        return redirect("/portfolio")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        print("aksjdaksd")
        user = current_user
        stocks = user.holdings
        print(user, stocks)
        return render_template("sell.html", stocks=stocks)

@investing.route("/sell/<string:symbol>")
@login_required
def sell_symbol(symbol):
    user = current_user
    stocks = user.holdings
    print(user, stocks)
    return render_template("sell.html", stocks=stocks, symbol=escape(symbol))