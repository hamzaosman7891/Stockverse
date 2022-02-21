from flask import Blueprint

auth = Blueprint('auth', __name__)

@auth.route('/login')
def login():
    return"<p>Login1</p"

@auth.route('/logout')
def logout():
    return"<p>Logout</p"

@auth.route('/sign-up')
def sign_up():
    return"<p>Sign Up</p"