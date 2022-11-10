import os

from flask import Flask, render_template, request, redirect, url_for
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
    UserMixin,
)
from werkzeug.security import check_password_hash, generate_password_hash
from flask_sqlalchemy import SQLAlchemy
from wtforms import ValidationError
from flask_migrate import Migrate
from flask_bootstrap import Bootstrap5
from forms import LoginForm, RegistrationForm, NoteForm

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(
    basedir, "data.sqlite"
)
app.config["SECRET_KEY"] = "1f54c168d2b78208b9d64c2a9664c03433fcef20"

db = SQLAlchemy(app)
bootstrap = Bootstrap5(app)
migrate = Migrate(app, db)
login_manager = LoginManager()
# login_manager.login_view = 'login'
login_manager.init_app(app)


class User(UserMixin, db.Model):
    __tablename__ = "users"
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
        return "<User %r>" % self.username


class Note(db.Model):
    __tablename__ = "notes"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(16))
    label = db.Column(db.Text, db.ForeignKey("label.label_name"))
    content = db.Column(db.String(64))


class Label(db.Model):
    __tablename__ = "label"
    id = db.Column(db.Integer, primary_key=True)
    label_name = db.Column(db.String(16))


@app.route("/", methods=["GET", "POST"])
def index():
    note = Note()
    return render_template("index.html", note=note)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("note"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data.lower()).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            next = request.args.get("next")
            if next is None or not next.startswith("/"):
                next = url_for("note")
            return redirect(next)
    return render_template("login.html", form=form)


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.route("/register", methods=["GET", "POST"])
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


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))


@app.route("/note")
@login_required
def note():
    return render_template("note.html")


@app.route("/add_note", methods=["GET", "POST"])
@login_required
def add_note():
    form = NoteForm()
    if form.validate_on_submit():
        note = Note(
            title=form.title.data,
            content=form.content.data,
            label=form.label.data
        )
        db.session.add(note)
        db.session.commit()
        return redirect(url_for("login"))
    return render_template("add_note.html", form=form)
