from flask import Blueprint, render_template , request, flash, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
from .models import Users
from . import db
auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    """Log user in"""
    
    # Forget any user_id
    session.clear()
    
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        if not username:
            flash('must provide username', category='error')

        # Ensure password was submitted
        elif not password:
            flash('must provide password', category='error')

        else:
            current_user = Users.query.filter_by(username=username).first()
            if current_user:
                if check_password_hash(current_user.hash, password):
                    flash('Logged in successfully!', category='success')
                    session["user_id"] = current_user.id
                    return redirect(url_for('views.home'))
                else:
                    flash('Incorrect password, try again.', category='error')
            else:
                flash('Username does not exist.', category='error')
    return render_template("login.html")

@auth.route('/logout')
def logout():
    session.clear()
    flash('You were logged out', category='success')
    return redirect(url_for('auth.login'))


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':

        username = request.form.get('username')
        password = request.form.get('password')
        confirmation = request.form.get('confirmation')


        user = Users.query.filter_by(username=username).first()

        if not username:
            flash('must provide username', category='error')

        # Ensure password was submitted
        elif not password:
            flash('must provide password', category='error')
        
        elif not confirmation:
            flash('must provide password confirmation', category='error')

        if user:
            flash('username already exists.', category='error')
        
        elif len(username) < 4:
            flash('username must be greater than 3 characters.', category='error')

        elif password != confirmation:
            flash('Passwords don\'t match.', category='error')

        elif len(password) < 7:
            flash('Password must be at least 7 characters.', category='error')

        
        else:
            # Insert username in database
            new_user = Users(
                username = username,
                hash = generate_password_hash(password))
            db.session.add(new_user)
            db.session.flush()
                
            # log newly registered user in
            #id = db.session.query(Users.id).filter(Users.username == username).first()
            session["user_id"] = new_user.id
            
            # finalize changes to database
            db.session.commit()
            
            # Flash success message
            flash("Congratulation! You were successfully registered!", category='success')
            
            # Redirect user to home page
            
            return redirect(url_for('views.home'))

    # User reached route via GET (as by clicking a link or via redirect)
    return render_template("sign_up.html")