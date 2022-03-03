from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from flask_bootstrap import Bootstrap
from os import environ
from flask_nav import Nav
from flask_nav.elements import *
import dominate
from dominate.tags import *

from flask_login import (
    UserMixin,
    login_user,
    LoginManager,
    current_user,
    logout_user,
    login_required,
)

login_manager = LoginManager()
login_manager.session_protection = "strong"
login_manager.login_view = "login"
login_manager.login_message_category = "info"
db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
nav = Nav()

logo = img(src='./static/img/logo.png', height="50", width="50", style="margin-top:-15px")

topbar = Navbar(logo,
    View('Submit Article', 'submit_articles'),
    View('Articles', 'articles'),
)
debug = False
if environ["debug"] == "1":
    debug = True


def create_app():
    app = Flask(__name__)
    """if debug:
        import credentials
        app.secret_key = credentials.app_secret
        app.config['SQLALCHEMY_DATABASE_URI'] = environ["BETTER_DB_URL"] #"postgresql://ebbujurirdemwx:36bb1c06c42b36a0d332e4a01cae4ac7630f843f1b8fa88c21f5130454c1d6eb@ec2-52-5-1-20.compute-1.amazonaws.com:5432/d7rp2ua9kqp2kq" #"sqlite:///database.db"
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True"""
    app.secret_key = environ['APP_SECRET']
    app.config['SQLALCHEMY_DATABASE_URI'] = environ["BETTER_DB_URL"]
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

    login_manager.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    bootstrap = Bootstrap(app)
    nav.register_element('top', topbar)
    nav.init_app(app)
    return app
"""
if __name__ == '__main__':
   create_app().run(debug = True)"""