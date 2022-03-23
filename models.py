from app import db
from flask_login import UserMixin




class User(UserMixin, db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    pwd = db.Column(db.String(300), nullable=False)
    groups = db.Column(db.String(1000))
    email_verified = db.Column(db.Boolean(), default = False)

    def __repr__(self):
        return '<User %r>' % self.username

class Articles(db.Model):
    __tablename__ = "articles"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300), nullable=False)
    link = db.Column(db.String(120), nullable=False)
    comment = db.Column(db.String(300))
    date = db.Column(db.DateTime())
    category = db.Column(db.String(300))
    username = db.Column(db.String(300), nullable=False)
    groups = db.Column(db.String(300))

class Groups(db.Model):
    __tablename__ = "groups"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    pwd = db.Column(db.String(300), nullable=False)
    creator = db.Column(db.String())
    members = db.Column(db.String())
    notifs = db.Column(db.String())