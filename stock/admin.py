import re

from flask import Blueprint, render_template, session, request, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
from .help import login_required
from . import db
from .models import Users, Transactions

admin = Blueprint('admin', __name__)

@admin.route("/account", methods = ["GET", "POST"])
@login_required
def account():
    user_id = session.get("user_id")

    if request.method == "POST":

        username = request.form.get("newname")
        password = request.form.get("newpass")
        confirmation = request.form.get("confpass")

        if username or password:
            if password:
                if not re.match("(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9])(?=.*(&|%|#)).{8,}", password):
                    flash("Password must contain at least one number, one uppercase and lowercase letter, one special symbol (&,$,#) and has at least 8 characters", category='error')
                    return redirect(url_for('admin.account'))
                if password != confirmation or not confirmation:
                    flash("Confirmation does not match password")
                    return redirect(url_for('admin.account'))
                
                cur_user = Users.query.filter(Users.id == user_id).first()
                cur_user.hash = generate_password_hash(password)
                db.session.commit()

            if username:
                if Users.query.filter(Users.username == username, Users.id != user_id).first() is not None:
                    flash("Username already exists", category='error')
                    return redirect(url_for('admin.account'))
                
                cur_user = Users.query.filter(Users.id == user_id).first()
                cur_user.username = username
                db.session.commit()

                flash("Your username / password were changed", category='success')
                return redirect(url_for('views.home'))

        else:
            flash("Your username / password were not changed", category='success')
            return redirect(url_for('admin.account'))
    else:
        user = db.session.query(Users.username, Users.cash).filter(Users.id == user_id)
        return render_template("account.html", user = user)

@admin.route("/changefund", methods = ["POST"])
@login_required
def changefund():
    user_id = session.get("user_id")

    if request.method == "POST":
        operation = request.form.get("cashop")
        amount = int(request.form.get("amount"))

        if not amount or amount < 0:
            flash("Please enter amount of cash you would like to add / withdraw a a positive number", category='error')
            return redirect(url_for('admin.account'))

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
                return redirect(url_for('admin.account'))
            new_amount = current.cash - amount

        current.cash = new_amount
        db.session.commit()

        flash("You successfully withdrew funds from your account", category='error')
        return redirect(url_for('views.home'))
    
    else:
        return redirect(url_for('admin.account'))

