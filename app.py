# squiblib.com

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from flask_bootstrap import Bootstrap
from flask_talisman import Talisman
from os import environ
from flask_nav import Nav
from flask_nav.elements import *
from flask_recaptcha import ReCaptcha
from flask_mail import Mail
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
    Talisman(app,content_security_policy=None)
    app.config.update(dict(
        MAIL_SERVER='smtp.gmail.com',
        MAIL_PORT=587,
        MAIL_USE_TLS=True,
        MAIL_USE_SSL=False,
        MAIL_USERNAME=environ["MAIL_USERNAME"],
        MAIL_PASSWORD=environ["MAIL_PASSWORD"],
    ))

    app.secret_key = environ['APP_SECRET']
    app.config['SQLALCHEMY_DATABASE_URI'] = environ["BETTER_DB_URL"]
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

    app.config['RECAPTCHA3_PUBLIC_KEY'] = environ["SITE_KEY_CAPTCHA"]
    app.config['RECAPTCHA3_PRIVATE_KEY'] = environ["SECRET_KEY_CAPTCHA"]
    recaptcha = ReCaptcha(app)

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