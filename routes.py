from flask import (
    Flask,
    render_template,
    redirect,
    flash,
    url_for,
    session
)
import datetime
from datetime import timedelta
from sqlalchemy.exc import (
    IntegrityError,
    DataError,
    DatabaseError,
    InterfaceError,
    InvalidRequestError,
)
from werkzeug.routing import BuildError

import requests

from bs4 import BeautifulSoup

from flask_bcrypt import Bcrypt, generate_password_hash, check_password_hash

from flask_login import (
    UserMixin,
    login_user,
    LoginManager,
    current_user,
    logout_user,
    login_required,
)

from app import create_app, db, login_manager, bcrypt
from models import User, Articles, Groups
from forms import login_form, register_form, submitArticle, createGroup, joinGroup


def get_title(url):
    with requests.Session() as session:
        s = session.get(url)
        soup = BeautifulSoup(s.text, 'html.parser')
        return (soup.title.string)


def add_to_group(user, group):
    if user.groups:
        groups = user.groups
        group_list = groups.split(",")
        if group not in group_list:
            group_list.append(group)
            user.groups = ','.join(group_list)
            flash("Successfuly joined {}".format(group), "success")
            return True
        else:
            flash("You are already in this group!", "danger")
    else:
        user.groups = group
        flash("Successfuly joined {}".format(group), "success")
        return True


def get_groups(groups):
    group_list = groups.split(",")
    return group_list


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


app = create_app()


# Home route
@app.route("/", methods=("GET", "POST"), strict_slashes=False)
def index():
    return render_template("index.html", title="Home")


# Login route
@app.route("/login/", methods=("GET", "POST"), strict_slashes=False)
def login():
    form = login_form()
    # email1 = form.get('email')
    print(form.email.data)
    if form.validate_on_submit():
        try:
            user = User.query.filter_by(email=form.email.data).first()
            if user:
                if check_password_hash(user.pwd, form.pwd.data):
                    login_user(user)
                    return redirect(url_for('index'))
                else:
                    flash("Invalid Username or password!", "danger")
            else:
                flash("Invalid Username or password!", "danger")
        except Exception as e:
            flash(e, "danger")
    return render_template("auth.html", form=form, btn_action="Go", text="Sign In")


# Register route
@app.route("/register/", methods=("GET", "POST"), strict_slashes=False)
def register():
    form = register_form()
    if form.validate_on_submit():
        try:
            email = form.email.data
            pwd = form.pwd.data
            username = form.username.data

            newuser = User(
                username=username,
                email=email,
                pwd=bcrypt.generate_password_hash(pwd),
            )

            db.session.add(newuser)
            db.session.commit()
            flash(f"Account Succesfully created", "success")
            return redirect(url_for("login"))


        except InvalidRequestError:
            db.session.rollback()
            flash(f"Something went wrong!", "danger")
        except IntegrityError:
            db.session.rollback()
            flash(f"User already exists!", "warning")
        except DataError:
            db.session.rollback()
            flash(f"Invalid Entry", "warning")
        except InterfaceError:
            db.session.rollback()
            flash(f"Error connecting to the database", "danger")
        except DatabaseError:
            db.session.rollback()
            flash(f"Error connecting to the database", "danger")
        except BuildError:
            db.session.rollback()
            flash(f"An error occured !", "danger")
    return render_template("auth.html", form=form,
                           text="Create account",
                           title="Register",
                           btn_action="Register account")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


# Home route
@app.route("/submit-article", methods=("GET", "POST"), strict_slashes=False)
def submit_articles():
    groups_list = get_groups(current_user.groups)
    form = submitArticle()
    form.group.choices = groups_list
    if form.validate_on_submit():
        try:
            link = form.link.data
            title = get_title(link)
            comment = form.comment.data
            category = form.category.data
            username = current_user.username
            date = datetime.datetime.utcnow()
            group = form.group.data
            print(date.strftime("%A, %b %d, %Y, %I:%M %p"))
            print(title, link, comment, category, username)

            newarticle = Articles(
                title=title,
                link=link,
                comment=comment,
                category=category,
                username=username,
                groups=group,
                date=date
            )

            db.session.add(newarticle)
            db.session.commit()
            flash(f"Article Succesfully Submitted", "success")
            return redirect(url_for('articles'))
        except Exception as e:
            db.session.rollback()
            flash(e, "danger")
    return render_template("submitArticle.html", title="Result", form=form)


@app.route("/articles", methods=("GET", "POST"), strict_slashes=False)
def articles():
    queries = []
    for group in get_groups(current_user.groups):
        queries.append([group, Articles.query.filter_by(groups=group).order_by(Articles.id.desc()).all()])
    return render_template("articles.html", queries=queries)  # , query1 = Articles.query.order_by(Articles.id.desc()))


@app.route("/create-group", methods=("GET", "POST"), strict_slashes=False)
def create_group():
    form = createGroup()
    if form.validate_on_submit():
        try:
            name = form.group_name.data
            pwd = form.password.data
            newgroup = Groups(
                name=name,
                pwd=bcrypt.generate_password_hash(pwd)
            )
            db.session.add(newgroup)
            user = User.query.filter_by(username=current_user.username).first()

            add_to_group(user, name)

            db.session.commit()
            flash(f"Group Successfully Created", "success")
            return redirect(url_for("articles"))
        except IntegrityError:
            db.session.rollback()
            flash(f"Group name already exists!", "warning")
            return redirect(url_for("create_group"))
        except Exception as e:
            db.session.rollback()
            flash(e, "danger")
            return redirect(url_for("create_group"))
    return render_template("createGroup.html", title="Create Group", form=form)


@app.route("/join-group", methods=("GET", "POST"), strict_slashes=False)
def join_group():
    form = joinGroup()
    if form.validate_on_submit():
        try:
            name = form.group_name.data
            pwd = form.password.data
            group = Groups.query.filter_by(name=name).first()
            if group:
                if check_password_hash(group.pwd, pwd):
                    user = User.query.filter_by(username=current_user.username).first()
                    if add_to_group(user, name):
                        db.session.commit()
                        return redirect(url_for('articles'))
                    else:
                        db.session.commit()
                        return redirect(url_for('join_group'))
                else:
                    flash("Incorrect password.", "danger")
            else:
                flash("Couldn't find that group.", "danger")
        except Exception as e:
            db.session.rollback()
            flash(e, "danger")
            return redirect(url_for("create_group"))
    return render_template("joinGroup.html", title="Join Group", form=form)


@app.route('/groups/<group>')
def single_group(group):
    query = Articles.query.filter_by(groups=group).order_by(Articles.id.desc()).all()
    if query:
        return render_template("singleGroup.html", query=query,group=group)
    else:
        return "Group not found"


if __name__ == "__main__":
    debug = False
    if debug:
        app.run(debug=True)
    else:
        app.run(debug=False)
