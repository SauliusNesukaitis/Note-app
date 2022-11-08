import os

from flask import Flask, render_template
from wtforms import SubmitField, StringField, PasswordField
from wtforms.validators import DataRequired, Length, Regexp, EqualTo
from flask_wtf import FlaskForm
from flask_bootstrap import Bootstrap5

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config["SECRET_KEY"] = "1f54c168d2b78208b9d64c2a9664c03433fcef20"

bootstrap = Bootstrap5(app)


class LoginForm(FlaskForm):
    email = StringField(
        "Username", validators=[DataRequired(), Length(1, 64)]
    )
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Log in")


class RegistrationForm(FlaskForm):
    username = StringField(
        "Username",
        validators=[
            DataRequired(),
            Length(1, 64),
            Regexp(
                '^[A-Za-z0-9][A-Za-z0-9_.]*$',
                0,
                'Usernames must have only letters, numbers, dots or ' 'underscores',
            ),
        ],
    )
    password = PasswordField(
        'Password',
        validators=[
            DataRequired(),
            EqualTo('password2', message='Passwords must match.'),
        ],
    )
    password2 = PasswordField("Confirm password", validators=[DataRequired()])
    submit = SubmitField("Register")


@app.route("/", methods=["GET", "POST"])
def index():
    form = LoginForm()
    return render_template("index.html", form=form)


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    return render_template("index.html", form=form)
