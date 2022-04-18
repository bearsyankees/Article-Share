from flask import (
    Flask,
    render_template,
    redirect,
    flash,
    url_for,
    session,
    abort,
    Markup
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

from flask_mail import Message, Mail

from app import create_app, db, login_manager, bcrypt, debug
from models import User, Articles, Groups
from forms import login_form, register_form, submitArticle, createGroup, joinGroup, resendVerification
from itsdangerous import URLSafeTimedSerializer


app = create_app()

ts = URLSafeTimedSerializer(app.config["SECRET_KEY"])

def get_title(url):
    with requests.Session() as session:
        s = session.get(url)
        soup = BeautifulSoup(s.text, 'html.parser')
        return (soup.title.string)


def add_to_group(user, group, notifs, new = False):
    if user.groups:
        groups = user.groups
        group_list = get_groups(groups)
        if group not in group_list or new:
            adding_group = Groups.query.filter_by(name=group).first().members
            members_list = get_members(adding_group)
            group_list.append(group)
            user.groups = ','.join(group_list)
            members_list.append(user.username)
            Groups.query.filter_by(name=group).first().members = ','.join(members_list)
            if notifs:
                notif_adding_group = Groups.query.filter_by(name=group).first().notifs
                notif_list = get_members(notif_adding_group)
                notif_list.append(user.username)
                Groups.query.filter_by(name=group).first().notifs = ','.join(notif_list)
            flash("Successfuly joined {}".format(group), "success")
            return True
        else:
            flash("You are already in this group!", "danger")
    else:
        user.groups = group
        adding_group = Groups.query.filter_by(name=group).first().members
        members_list = get_members(adding_group)
        members_list.append(user.username)
        Groups.query.filter_by(name=group).first().members = ','.join(members_list)
        if notifs:
            notif_adding_group = Groups.query.filter_by(name=group).first().notifs
            notif_list = get_members(notif_adding_group)
            notif_list.append(user.username)
            Groups.query.filter_by(name=group).first().notifs = ','.join(notif_list)
        flash("Successfuly joined {}".format(group), "success")
        return True


def get_members(members):
    if members:
        members_list = members.split(",")
        members_list1 = [member for member in members_list if User.query.filter_by(username=member).all()]
        return members_list1
    else:
        return []

def leave_group(group_to_leave,groups, deletion = False):
    group_instance = Groups.query.filter_by(name=group_to_leave).first()
    group_list = get_groups(groups)
    group_list1 = [group for group in group_list if Groups.query.filter_by(name=group).all() and group != group_to_leave]
    notif_list = get_members(group_instance.notifs)
    notif_list1 = [member for member in notif_list if member != current_user.username]
    member_list = get_members(group_instance.members)
    member_list1 = [member for member in member_list if member != current_user.username]
    group_instance.notifs = ','.join(notif_list1)
    group_instance.members = ','.join(member_list1)
    if not deletion:
        db.session.commit()
        current_user.groups = group_list1
    else:
        db.session.commit()
        return group_list1

def delete_group(group):
    for user in get_members(Groups.query.filter_by(name=group).first().members):
        print(user)
        User.query.filter_by(username=user).first().groups = leave_group(group,User.query.filter_by(username=user).first().groups,deletion = True)

    Articles.query.filter_by(groups = group).delete()
    Groups.query.filter_by(name=group).delete()

def send_post_notifications(recipients, title, poster, link, group, sender = "notifications@squiblib.com"):
    msg = Message(
        'New article from {}.'.format(poster),
        sender=sender,
        bcc=recipients)
    msg.body = "This is the email body"
    msg.html = '<b>{} just shared this article in your group</b> <a href={}>{}</a>! ' \
               '<br>  <a href={}>{}</a>'.format(poster,url_for("single_group",group = group), group, link, title)
    mail = Mail(app)
    with app.app_context():
        mail.send(msg)

def alter_notifs(on, group):
    try:
        if on:
            notif_adding_group = Groups.query.filter_by(name=group).first().notifs
            notif_list = get_members(notif_adding_group)
            notif_list.append(current_user.username)
            Groups.query.filter_by(name=group).first().notifs = ','.join(notif_list)
        if not on:
            print("noo")
            notif_adding_group = Groups.query.filter_by(name=group).first().notifs
            notif_list = get_members(notif_adding_group)
            print(notif_list)
            notif_list = [member for member in notif_list if member != current_user.username]
            print(notif_list)
            Groups.query.filter_by(name=group).first().notifs = ','.join(notif_list)
        db.session.commit()
    except:
        db.session.rollback()
        flash(f"An error occured !", "danger")


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.template_global()
def get_groups(groups):
    if groups:
        fixdic = groups.replace("{","")
        fixdic = fixdic.replace("}", "")
        group_list = fixdic.split(",")
        group_list1 = [group for group in group_list if Groups.query.filter_by(name=group).all()]
        return group_list1
    return None

@app.template_global()



# Home route
@app.route("/", methods=("GET", "POST"), strict_slashes=False)
def index():
        return redirect(url_for("articles"))

# Login route
@app.route("/login/", methods=("GET", "POST"), strict_slashes=False)
def login():
    if current_user.is_authenticated:
        return redirect(url_for("articles"))
    form = login_form()
    # email1 = form.get('email')
    print(form.email.data)
    if form.validate_on_submit():
        try:
            user = User.query.filter_by(email=form.email.data.lower()).first()
            if not user:
                user = User.query.filter_by(username=form.email.data.lower()).first()
            if user:
                if check_password_hash(user.pwd, form.pwd.data):
                    if user.email_verified:
                        login_user(user)
                        return redirect(url_for('articles'))
                    else:
                        flash(Markup("Account not verified! Click <a href=\"{}\" class=\"alert-link\">here</a> to resend"
                              " verification email.".format(url_for("send_confirmation_email"))), "danger")
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
            email = form.email.data.lower()
            pwd = form.pwd.data
            username = form.username.data.lower()

            newuser = User(
                username=username,
                email=email,
                pwd=bcrypt.generate_password_hash(pwd).decode('utf8'),
            )

            db.session.add(newuser)
            db.session.commit()
            msg = Message(
                'Welcome to SquibLib, {}, please confirm your email'.format(username),
                sender='notifications@squiblib.com',
                recipients=[email])

            token = ts.dumps(email, salt='email-confirm-key')

            confirm_url = url_for(
                'confirm_email',
                token=token,
                _external=True)

            html = render_template(
                'email/activate.html',
                confirm_url=confirm_url)

            msg.html = html
            mail = Mail(app)
            with app.app_context():
                mail.send(msg)
            flash(f"Thanks for signing up! Please check your email ({email}) to verify your account.", "warning")
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
@login_required
def submit_articles():
    groups_list = get_groups(current_user.groups)
    if groups_list:
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
                print(title, link, comment, category, username,group,date)

                newarticle = Articles(
                    title=title,
                    link=link,
                    comment=comment,
                    category=category,
                    username=username,
                    groups=group,
                    date=date
                )
                print(newarticle)
                #recipients = [member.email for member in get_members(Groups.query.filter_by(groups=group).first().notifs):
                recipients = [member[0].email for member in
                              [User.query.filter_by(username=member).all() for member in get_members(
                                  Groups.query.filter_by(name=group).first().notifs)]]
                send_post_notifications(recipients,title,current_user.username,link,group)
                db.session.add(newarticle)
                db.session.commit()
                flash(f"Article Succesfully Submitted", "success")
                return redirect(url_for('articles'))
            except Exception as e:
                db.session.rollback()
                flash(e, "danger")
        return render_template("submitArticle.html", title="Result", form=form)
    else:
        flash("Seems like you aren't part of any groups yet!","warning")
        return redirect(url_for('join_group'))

@app.route("/articles", methods=("GET", "POST"), strict_slashes=False)
@login_required
def articles():
    queries = []
    groups = get_groups(current_user.groups)
    if groups:
        for group in groups:
            queries.append([group, Articles.query.filter_by(groups=group).order_by(Articles.id.desc()).all()])

        return render_template("articles.html", queries=queries, groups = groups)  # , query1 = Articles.query.order_by(Articles.id.desc()))
    else:
        flash("Seems like you aren't part of any groups yet!","warning")
        return redirect(url_for('join_group'))

@app.route("/create-group", methods=("GET", "POST"), strict_slashes=False)
@login_required
def create_group():
    form = createGroup()
    if form.validate_on_submit():
        try:
            name = form.group_name.data
            pwd = form.password.data
            notifs = form.notifs.data
            newgroup = Groups(
                name=name,
                pwd=bcrypt.generate_password_hash(pwd).decode('utf8'),
                creator = current_user.username
            )
            db.session.add(newgroup)
            #db.session.commit()
            user = User.query.filter_by(username=current_user.username).first()
            add_to_group(user, name, notifs, new = True)

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
@login_required
def join_group():
    form = joinGroup()
    if form.validate_on_submit():
        try:
            name = form.group_name.data
            pwd = form.password.data
            notifs = form.notifs.data
            print(notifs)
            group = Groups.query.filter_by(name=name).first()
            if group:
                if check_password_hash(group.pwd, pwd):
                    user = User.query.filter_by(username=current_user.username).first()
                    if add_to_group(user, name, notifs):
                        db.session.commit()
                        return redirect(url_for('single_group', group=name))
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
@login_required
def single_group(group):
    owner = False
    if Groups.query.filter_by(name=group).all():
        if current_user.groups:
            if group in get_groups(current_user.groups):
                query = Articles.query.filter_by(groups=group).order_by(Articles.id.desc()).all()
                if current_user.username == Groups.query.filter_by(name=group).first().creator:
                    owner = True
                if current_user.username in Groups.query.filter_by(name=group).first().notifs.split(",") or current_user.username == Groups.query.filter_by(name=group).first().notifs:
                    notifs_on = "off"
                    notifs_to_pass = False
                else:
                    notifs_on = "on"
                    notifs_to_pass = True
                return render_template("singleGroup.html", query=query, group=group, title=group, groups = get_groups(current_user.groups), owner=owner, notifs_on = notifs_on, ntp = notifs_to_pass)
            else:
                return "Sorry, you are not part of this group"
        else:
            return "You aren't part of any groups yet!"
    else:
        return "Group not found"

@app.route('/delete/<group>',methods =['POST'])
@login_required
def deletegroups(group):
    try:
        if current_user.username == Groups.query.filter_by(name=group).first().creator:
            delete_group(group)
            db.session.commit()
            flash("Successfuly deleted {}!".format(group) , "success")
            return redirect(url_for("articles"))
    except Exception as e:
        db.session.rollback()
        flash(e, "danger")
        return redirect(url_for("articles"))

@app.route('/leave/<group>',methods =['POST'])
@login_required
def leavegroup(group):
    try:
        leave_group(group_to_leave=group,groups = current_user.groups)
        db.session.commit()
        flash("Successfuly left {}!".format(group) , "success")
        return redirect(url_for("articles"))
    except Exception as e:
        db.session.rollback()
        flash(e, "danger")
        return redirect(url_for("articles"))

@app.route('/favicon.ico')
def favicon():
    return app.send_static_file('favicon.ico')

@app.route('/confirm/<token>')
def confirm_email(token):
    try:
        email = ts.loads(token, salt="email-confirm-key", max_age=86400)
    except:
        abort(404)

    user = User.query.filter_by(email=email).first_or_404()

    user.email_verified = True
    db.session.commit()
    return redirect(url_for('login'))

@app.route('/send-confirmation-email', methods = ["GET", "POST"])
def send_confirmation_email():
    form = resendVerification()
    if form.validate_on_submit():
        email = form.email.data
        user = User.query.filter_by(email=email).first()
        if user:
            print(user.username,"ye")
            msg = Message(
            'Welcome to SquibLib, {}, please confirm your email'.format(user.username),
            sender='notifications@squiblib.com',
            recipients=[email])

            token = ts.dumps(email, salt='email-confirm-key')

            confirm_url = url_for(
                'confirm_email',
                token=token,
                _external=True)

            html = render_template(
                'email/activate.html',
                confirm_url=confirm_url)

            msg.html = html
            mail = Mail(app)
            with app.app_context():
                mail.send(msg)
        flash("Verification email sent.", "success")
        return redirect(url_for('login'))

    return render_template("verification.html", form=form, btn_action="Go")

@app.route('/alter/<group>/<ntp>')
@login_required
def alter(group, ntp):
    if ntp == "False":
        ntp = False
    else:
        ntp = True
    print(ntp)
    alter_notifs(ntp,group)
    return redirect(url_for("single_group", group = group))

@app.route('/profile')
@login_required
def profile():
    return "Coming soon, {}".format(current_user.username)

if __name__ == "__main__":
    if debug:
        app.run(debug=True)

    else:
        app.run(debug=False)
