from flask import Blueprint, render_template, request, redirect, flash, session, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func, label
from . import db
from .models import Users, Transactions
from .help import lookup, usd, login_required


views = Blueprint('views', __name__)

@views.route('/')
def landing():
    return render_template("index.html")

@views.route('/home')
@login_required
def home():
    
    user_id = session.get("user_id")
    # get suitable order direction SQLAlchemy object based on passed sort_order 

    holdings = db.session.query(Transactions.symbol, Transactions.name,Transactions.price,
                                func.sum(Transactions.number).label('shares'),
                                func.sum(Transactions.amount).label('total'),
                                (func.sum(Transactions.amount) / func.sum(Transactions.number)).label('avgprice')).\
                                filter(Transactions.user_id == user_id).\
                                group_by(Transactions.symbol).\
                                having(func.sum(Transactions.number) != 0).all()
    
    fund = Users.query.filter(Users.id == user_id).first()
    funds = float(fund.cash)
    
    if holdings == []:
        return render_template("home.html", cash = funds, total = [], shares = [], price = [], avgprice = [], symbols = [], holdings_length = 0)
    
    else:
        # Calculate symbol list length for iteration in index.html
        holdings_length = len(holdings)
        #print("holdings_length: ", holdings_length)
        
        # Create empty arrays to store values
        symbols = []
        price = []
        avgprice = []
        shares = []
        total = []
        # Calculate value of each holding of stock in portfolio
        for i in range(len(holdings)):
            symbol_index = holdings[i].symbol
            #print("symbol_index:", symbol_index)
            symbols.append(symbol_index)
            # Obtain price of stock using iex API
            price_index = float(lookup(symbol_index).get('price'))
            price.append(price_index)

            avgprice_index = holdings[i].avgprice
            #print("price_index:", price_index)
            avgprice.append(avgprice_index)
            #for i in range(len(holdings)):
            shares_index = holdings[i].shares
            #print("shares_index:", shares_index)
            shares.append(shares_index)
            
            calc = shares_index * avgprice_index
            #print("calc:", calc)
            total.append(calc)

        # Render page with information
        return render_template("home.html", holdings = holdings, holdings_length = holdings_length, price = price, avgprice = avgprice, shares=shares,  total = total, cash = funds)
    


@views.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        symbol = request.form.get("symbol")
        
        # load quote page again if symbol is not provided
        if not symbol:
            flash("Please enter stock ticker symbol", category='error')
            return redirect(url_for('views.quote'))
        
        # request symbol info from IEX cloud
        quoteInfo = lookup(symbol)
        
        if quoteInfo is None:
            flash("The symbol was not found.", category='error')
            return redirect(url_for('views.quote'))
        
        # Redirect user to page with stock ticker(-s) info
        return render_template("quote.html", symbol = quoteInfo["symbol"], name = quoteInfo["name"], price = usd(quoteInfo["price"]), marketCap = usd(quoteInfo["marketCap"]), YTDChange = usd(quoteInfo["YTDChange"]), WK52High = usd(quoteInfo["WK52High"]), WK52Low = usd(quoteInfo["WK52Low"]))
    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("quote.html" )


@views.route("/graph")
@login_required
def graph():
    
    user_id = session.get("user_id")
    # get suitable order direction SQLAlchemy object based on passed sort_order 
    
    holdings = db.session.query(Transactions.symbol, Transactions.name,Transactions.price,
                                func.sum(Transactions.number).label('shares'),
                                func.sum(Transactions.amount).label('total'),
                                (func.sum(Transactions.amount) / func.sum(Transactions.number)).label('avgprice')).\
                                filter(Transactions.user_id == user_id).\
                                group_by(Transactions.symbol).\
                                having(func.sum(Transactions.number) != 0).all()
    
    fund = Users.query.filter(Users.id == user_id).first()
    funds = float(fund.cash)
    
    if holdings == []:
        return render_template("graph.html", cash = funds, total = [], shares = [], avgprice = [], price = [], symbols = [], holdings_length = 0)
    
    else:
        # Calculate symbol list length for iteration in index.html
        holdings_length = len(holdings)
        #print("holdings_length: ", holdings_length)
        
        # Create empty arrays to store values
        symbols = []
        price = []
        avgprice = []
        shares = []
        total = []
        # Calculate value of each holding of stock in portfolio
        for i in range(len(holdings)):
            symbol_index = holdings[i].symbol
            #print("symbol_index:", symbol_index)
            symbols.append(symbol_index)
            # Obtain price of stock using iex API
           #price_index = float(lookup(symbol_index).get('price'))
            price_index = holdings[i].price
            #print("price_index:", price_index)
            price.append(price_index)

            avgprice_index = holdings[i].avgprice
            #print("price_index:", price_index)
            avgprice.append(avgprice_index)
            #for i in range(len(holdings)):
            shares_index = holdings[i].shares
            #print("shares_index:", shares_index)
            shares.append(shares_index)
            
            calc = shares_index * avgprice_index
            #print("calc:", calc)
            total.append(calc)

        # Render page with information
        return render_template("graph.html", holdings = holdings, holdings_length = holdings_length, symbols= symbols, price = price, avgprice = avgprice, usd = usd , shares=shares,  total = total, cash = funds)


@views.route("/changefund", methods = ["POST"])
@login_required
def changefund():
    user_id = session.get("user_id")

    if request.method == "POST":
        operation = request.form.get("cashop")
        amount = int(request.form.get("amount"))

        if not amount or amount < 0:
            flash("Please enter amount of cash you would like to add / withdraw as a positive number", category='error')
            return redirect(url_for('views.home'))
            
        current = Users.query.filter(Users.id == user_id).first()
            
        if operation == "add":
            new_amount = current.cash + amount
            current.cash = new_amount
            db.session.commit()
            flash("You successfully added funds to your account", category='success')
            return redirect(url_for('views.home'))
            
        if operation == "withdraw":
            if amount > current.cash:
                flash("The amount of cash in your account is not enough", category='error')
                return redirect(url_for('views.home'))
            new_amount = current.cash - amount
            
            current.cash = new_amount
            db.session.commit()

        flash("You successfully withdrew funds from your account", category='error')
        return redirect(url_for('views.home'))
    
    else:
        return redirect(url_for('views.home'))