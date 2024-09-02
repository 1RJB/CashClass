import os
from flask import Flask, flash, redirect, render_template, request, session
from markupsafe import escape
from datetime import datetime
from util import lookup
from flask_login import (
    current_user,
    login_required,
)
from models import User, Holding, Transaction


@app.route("/buy", methods=["GET", "POST"])
# @login_required
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
            user_id=user.id,
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
        found_holding = Holding.query.filter((Holding.user_id == user.id) & (Holding.symbol == new_transaction.symbol)).first()

        # Add stock to holdings if not already owned
        if found_holding == None:
            new_holding = Holding(
                user_id=user.id,
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


@app.route("/buy/<string:symbol>")
@login_required
def buy_symbol(symbol):
    return render_template("buy.html", symbol=escape(symbol))


@app.route("/sell", methods=["GET", "POST"])
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
        holding = Holding.query.filter((Holding.user_id==user.id) & (Holding.symbol==quote["symbol"])).first()

        # Check if user owns shares of stock user wants to sell
        if holding == None:
            return render_template("sell.html", error="You do not own shares in this company"), 400

        # Check if user owns enough shares user intends to sell
        elif holding.shares < int(request.form.get("shares")):
            return render_template("sell.html", error="You do not own that many shares to sell"), 400

        # Record transaction
        new_transaction = Transaction(
            user_id=user.id,
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
        user = current_user
        stocks = user.holdings

        return render_template("sell.html", stocks=stocks)


@app.route("/sell/<string:symbol>")
@login_required
def sell_symbol(symbol):
    user = current_user
    stocks = user.holdings

    return render_template("sell.html", stocks=stocks, symbol=escape(symbol))