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
    return render_template("home.html")
    


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

