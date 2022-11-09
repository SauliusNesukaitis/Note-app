import os

from flask import Flask, render_template, request, redirect, url_for
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash
from flask_sqlalchemy import SQLAlchemy
from wtforms import SubmitField, StringField, PasswordField, ValidationError
from wtforms.validators import DataRequired, Length, Regexp, EqualTo
from flask_wtf import FlaskForm
from flask_migrate import Migrate
from flask_bootstrap import Bootstrap5

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
    os.path.join(basedir, 'data.sqlite')
app.config["SECRET_KEY"] = "1f54c168d2b78208b9d64c2a9664c03433fcef20"

db = SQLAlchemy(app)
bootstrap = Bootstrap5(app)
migrate = Migrate(app, db)


class LoginForm(FlaskForm):
    username = StringField(
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

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError("Username already in use.")


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    # password = db.Column(db.String(128))

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def validate_password(self, field):
        if len(field.data) < self.passwd_min_len:
            raise ValidationError(
                f"Password minimum length should be at least {self.passwd_min_len} characters"
            )

    @property
    def password(self):
        raise AttributeError("password is not a readable attribute")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def __repr__(self):
        return '<User %r>' % self.username


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data.lower()).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            next = request.args.get("next")
            if next is None or not next.startswith("/"):
                next = url_for("main.index")
            return redirect(next)
    return render_template("login.html", form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            password=form.password.data,
        )
        db.session.add(user)
        db.session.commit()
        return redirect(url_for("login"))
    return render_template("register.html", form=form)
