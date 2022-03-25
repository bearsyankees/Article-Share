from wtforms import (
    StringField,
    PasswordField,
    URLField,
    SubmitField,
    BooleanField,
    IntegerField,
    DateField,
    TextAreaField,
    SelectField,
    widgets,

)

import re
from captcha import Recaptcha3Field
from flask_wtf import FlaskForm
from wtforms.validators import InputRequired, Length, EqualTo, Email, Regexp ,Optional, url
import email_validator
from flask_login import current_user
from wtforms import ValidationError,validators
from models import User


class register_form(FlaskForm):
    username = StringField(
        validators=[
            InputRequired(),
            Length(3, 20, message="Please provide a valid name"),
            Regexp(
                "^[A-Za-z][A-Za-z0-9_.]*$",
                0,
                "Usernames must have only letters, " "numbers, dots or underscores",
            ),
        ]
    )
    email = StringField(validators=[InputRequired(), Email(), Length(1, 64)])
    pwd = PasswordField(validators=[InputRequired(), Length(8, 72)])
    cpwd = PasswordField(
        validators=[
            InputRequired(),
            Length(8, 72),
            EqualTo("pwd", message="Passwords must match !"),
        ]
    )
    captcha = Recaptcha3Field(action="TestAction", execute_on_load=True)

class login_form(FlaskForm):
    email = StringField(validators=[InputRequired(), Email(), Length(1, 64)])
    pwd = PasswordField(validators=[InputRequired(), Length(min=8, max=72)])
    # Placeholder labels to enable form rendering
    username = StringField(
        validators=[Optional()]
    )

class submitArticle(FlaskForm):
    #title = StringField(validators=[InputRequired(message="Please enter a title.")])
    link = URLField(validators=[url()])
    comment = StringField()
    category = StringField()
    group = SelectField(u'Group to share with:', validators=[InputRequired()])
    submit = SubmitField('Post')

class createGroup(FlaskForm):
    group_name = StringField(validators=[InputRequired(), Length(1, 64)])
    password = PasswordField(validators=[InputRequired(), Length(min=8, max=72)])
    notifs = BooleanField("Do you want to receive email notifications when a new article is posted to your group?")
    submit = SubmitField('Create')

class joinGroup(FlaskForm):
    group_name = StringField(validators=[InputRequired(), Length(1, 64)])
    password = PasswordField(validators=[InputRequired(), Length(min=8, max=72)])
    notifs = BooleanField("Do you want to receive email notifications when a new article is posted in this group?")
    submit = SubmitField('Join')

class resendVerification(FlaskForm):
    email = StringField(validators=[InputRequired(), Email(), Length(1, 64)])
    submit = SubmitField('Send')




