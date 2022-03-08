from flask import Blueprint, render_template, request, redirect, flash, session, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func, label
from . import db
from .models import Users, Transactions
from .help import lookup, usd, login_required


views = Blueprint('views', __name__)

@views.route('/')
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
        return render_template("home.html", cash = funds, total = [], shares = [], price = [], symbols = [], holdings_length = 0)
    
    else:
        # Calculate symbol list length for iteration in index.html
        holdings_length = len(holdings)
        #print("holdings_length: ", holdings_length)
        
        # Create empty arrays to store values
        symbols = []
        price = []
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
            #for i in range(len(holdings)):
            shares_index = holdings[i].shares
            #print("shares_index:", shares_index)
            shares.append(shares_index)
            
            calc = shares_index * price_index
            #print("calc:", calc)
            total.append(calc)

        # Render page with information
        return render_template("home.html", holdings = holdings, holdings_length = holdings_length, price = price, shares=shares,  total = total, cash = funds)
    


@views.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        symbol = request.form.get("symbol")
        
        # load quore page again if symbol is not provided
        if not symbol:
            flash("Please enter stock ticker symbol", category='error')
            return redirect(url_for('views.quote'))
        
        # request symbol info from IEX cloud
        quoteInfo = lookup(symbol)
        
        if quoteInfo is None:
            flash("The symbol was not found.", category='error')
            return redirect(url_for('views.quote'))
        
        # Redirect user to page with stock ticker(-s) info
        return render_template("quoted.html", symbol = quoteInfo["symbol"], name = quoteInfo["name"], price = usd(quoteInfo["price"]))
    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("quote.html")

