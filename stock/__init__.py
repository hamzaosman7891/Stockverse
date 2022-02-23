from flask import Flask
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from tempfile import mkdtemp
from os import path
import os

db = SQLAlchemy()
DB_NAME = "database.db"

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'hsjsuush sgsjs'

    app.config['STATIC_FOLDER'] = 'static'
    app.config['TEMPLATES_FOLDER'] = 'template'

    app.config['TEMPLATES_AUTO_RELOAD'] = True

    app.config['SESSION_FILE_DIR'] = mkdtemp()
    app.config['SESSION_PERMANENT'] = False
    app.config['SESSION_TYPE'] = 'filesystem'

    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    app.config['SQLALCHEMY_ECHO'] = True
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

     # Ensure responses aren't cached
    @app.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response

    # Initialize session
    Session(app)

    from .models import Users, Transactions
    
    
    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    create_database(app)

    return app

def create_database(app):
	if not path.exists('stock/' + DB_NAME):
		db.create_all(app=app)
		print('Creates Database!')

#api_key = os.getenv("API_KEY")

# Make sure API key is set
#if not os.environ.get("API_KEY"):
    #raise RuntimeError("API_KEY not set")

