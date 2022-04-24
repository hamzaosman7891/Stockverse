from flask import Blueprint, render_template, session, request, redirect, flash, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func, label
from .help import lookup, usd, login_required
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

            current_user = Users.query.filter(Users.id == user_id).first()
            current_user.cash = cash_after
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

@transactions.route('/history')
@login_required
def history():
    user_id = session.get("user_id") 
    
    holdings = db.session.query(Transactions.symbol, Transactions.name,Transactions.price,Transactions.date,Transactions.number).\
                                filter(Transactions.user_id == user_id).all()


    
    if holdings == []:
        return render_template("history.html", date = [], shares = [], price = [], symbols = [], holdings_length = 0)
    
    else:
        # Calculate symbol list length for iteration
        holdings_length = len(holdings)
        #print("holdings_length: ", holdings_length)
        
        # Create empty arrays to store values
        symbols = []
        price = []
        shares = []
        date = []
        # Calculate value of each holding of stock in portfolio
        for i in range(len(holdings)):
            symbol_index = holdings[i].symbol
            #print("symbol_index:", symbol_index)
            symbols.append(symbol_index)
            # Obtain price of stock using iex API

        for i in range(len(holdings)):
            price_index = holdings[i].price
            #print("price_index:", price_index)
            price.append(price_index)


        for i in range(len(holdings)):
            shares_index = holdings[i].number
            #print("shares_index:", shares_index)
            shares.append(shares_index)
        
        for i in range(len(holdings)):
            date_index = holdings[i].date
            #print("date_index:", date_index)
            date.append(date_index)
        # Render page with information
        return render_template("history.html", holdings = holdings, holdings_length = holdings_length, price = price, shares = shares, date = date)


@transactions.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""

    user_id = session.get("user_id")

    # request a list of owned shares
    
    holdings = db.session.query(Transactions.symbol, Transactions.name,
                                func.sum(Transactions.number).label('shares'),
                                func.sum(Transactions.amount).label('total'),
                                (func.sum(Transactions.amount) / func.sum(Transactions.number)).label('avgprice')).\
                                filter(Transactions.user_id == user_id).\
                                group_by(Transactions.symbol).\
                                having(func.sum(Transactions.number) != 0).all()
    # return base sell page if no url variiables
    if not request.args and request.method == "GET":

        if holdings is not None:

            # prepare a list of owned shares to choose from
            list = []
            for row in holdings:
                list.append(row.symbol)
                

            # load sell page
            return render_template("sell.html", list = list)
            # return apology if user does not own any stock
            
        else:
            flash("You do not own any stock to sell", category='error')
            return redirect(url_for('transactions.buy'))



    # request stock ticker symbol from URL
    symbol = request.args.get("symbol", '')

    # no stock ticker symbol was provided via GET
    if not symbol:

        # User reached route via POST (as by submitting a form via POST)
        if request.method == "POST":

            symbol = request.form.get("symbol")
            name = request.form.get("name")
            shares = request.form.get("shares")
            price = float(request.form.get("price"))

            # load apology if symbol is not provided
            if not symbol:
                flash("Please choose ticker symbol of stock you want to sell", category='error')
                return redirect(url_for('transactions.sell'))

            # load apology if number is not provided
            if not shares or int(shares) <= 0:
                flash("Please enter positive number of shares to sell", category='error')
                return redirect(url_for('transactions.sell'))

            # get owned number of stocks
            for row in holdings:
                if symbol == row.symbol:
                    sharesOwned = row.shares
                    break

            # check number of shares available
            if int(shares) > sharesOwned:
                flash("Sorry, you do not own enough number of shares ", category='error')
                return redirect(url_for('transactions.sell'))
            
            # prepare data to be inserted into db
            amount = round(int(shares) * price, 2) * -1

            
            funds =  Users.query.filter(Users.id == user_id).first()
            cash_after = float(funds.cash) - amount

            # fill in transactions table with new data
            new_transaction = Transactions (
                user_id = user_id,
                symbol = symbol,
                name = name,
                number = int(shares) * - 1,
                price = price,
                amount = amount,
                type = "sell")
            db.session.add(new_transaction)
            db.session.commit()

            cur_user = Users.query.filter(Users.id == user_id).first()
            cur_user.cash = cash_after
            db.session.commit()

            flash("You've successfully sold " + str(shares) + " shares of " + symbol, category='success')
            #flash(message)
            return redirect(url_for("views.home"))

        else:
            flash("must enter stock ticker symbol", category='error')
            return redirect(url_for('transactions.sell'))

    # request symbol information from IEX cloud
    quoteInfo = lookup(symbol)

    # redirect to buy page with error message if no symbol was found
    if quoteInfo is None:
        flash("The symbol was not found or something else went wrong.", category='error')
        return redirect(url_for('transactions.buy'))

    # get number of owned stocks and average price of aquisition
    for row in holdings:
        if symbol == row.symbol:
            sharesOwned = row.shares
            avgPrice = row.avgprice
            amount = row.total
            break

    # load sell page with stock ticker information filled in
    return render_template("sell.html", quoteInfo = quoteInfo, sharesOwned = sharesOwned, avgPrice = avgPrice, amount = amount)