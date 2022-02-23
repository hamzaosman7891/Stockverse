from flask import Blueprint, render_template, session, request, redirect, flash, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func, label
from .help import lookup
from .help import usd
from .help import login_required
from . import db
from .models import Users, Transactions

transactions = Blueprint('transactions', __name__)

@transactions.route("/buy", methods=['GET', 'POST'])
@login_required
def buy():

    if not request.args and request.method =="GET":
        return render_template("buy.html")
    
    user_id = session.get("user_id")

    symbol = request.args.get("symbol", '')
    shares = request.args.get("shares", '')

    if not shares:
        shares = 0
        flash('Please enter a number of shares to buy.', category='error')
        return redirect(url_for('transactions.buy'))

    
    if int(shares) < 0:
        flash('Please enter positive number of shares to buy.', category='error')
        return redirect(url_for('transactions.buy'))
    
    fund = Users.query.filter(Users.id == user_id).first()
    funds = float(fund.cash)

    if not symbol:

        if request.method == "POST":

            symbol = request.form.get("symbol")
            name = request.form.get("name")
            shares = int(request.form.get("shares"))
            price = float(request.form.get("price"))

            if not symbol:
                flash("please enter stock ticker symbol", category='error')
                return redirect(url_for('transactions.buy'))

            if not shares or shares <= 0:
                flash("please enter postive number of shares to buy", category='error')
                return redirect(url_for('transactions.buy'))

            if funds < price * shares:
                flash("sorry, not enough funds for this transaction", category='error')
                return redirect(url_for('transactions.buy'))

            amount = round(shares * price, 2)
            cash_after = funds - amount

            new_transaction = Transactions (
                user_id = user_id,
                symbol = symbol,
                name = name,
                number = shares,
                price = price,
                amount = shares * price,
                type = "buy")
            db.session.add(new_transaction)
            db.session.commit()

            flash("You've successfully bought " + str(shares) + " shares of " + symbol, category='success')
            return redirect(url_for('views.home'))

        else:
            flash("Please enter stock ticker symbol.", category='error')
            return redirect(url_for('transactions.buy'))
    
    quoteInfo = lookup(symbol)

    if quoteInfo is None:
        flash("The symbol was not found", category='error')
        return redirect(url_for('transactions.buy'))
    
    return render_template("buy.html", quoteInfo = quoteInfo, shares = shares, price = quoteInfo["price"], cash = funds, required = quoteInfo["price"] * int(shares))

