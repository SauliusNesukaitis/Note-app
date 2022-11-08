import os

from flask import Flask, render_template, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from wtforms import SubmitField, StringField, PasswordField
from wtforms.validators import DataRequired, Length, Regexp, EqualTo
from flask_wtf import FlaskForm
from werkzeug.security import generate_password_hash, check_password_hash
from flask_bootstrap import Bootstrap5

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
    os.path.join(basedir, 'data.sqlite')
app.config["SECRET_KEY"] = "1f54c168d2b78208b9d64c2a9664c03433fcef20"

db = SQLAlchemy(app)
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


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))


    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User %r>' % self.username


@app.route('/', methods=['GET', 'POST'])
def index():
    form = LoginForm()
    return render_template('index.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    return render_template('index.html', form=form)
