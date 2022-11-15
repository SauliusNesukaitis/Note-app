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
from forms import (
    LoginForm,
    RegistrationForm,
    NoteForm,
    LabelForm,
    EditLabelForm,
    EditNoteForm,
    SearchForm,
    FilterForm,
)

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(
    basedir, "data.sqlite"
)
app.config["SECRET_KEY"] = "1f54c168d2b78208b9d64c2a9664c03433fcef20"
app.config["BOOTSTRAP_BOOTSWATCH_THEME"] = "cyborg"

db = SQLAlchemy(app)
bootstrap = Bootstrap5(app)
migrate = Migrate(app, db)
login_manager = LoginManager()
login_manager.init_app(app)


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    notes = db.relationship("Note", backref="author", lazy="dynamic")
    labels = db.relationship("Label", backref="author", lazy="dynamic")

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
        return f"User {self.username}"


class Note(db.Model):
    __tablename__ = "notes"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(16))
    content = db.Column(db.String(64))
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    label_id = db.Column(db.Integer, db.ForeignKey("labels.id"))


class Label(db.Model):
    __tablename__ = "labels"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(16))
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    notes = db.relationship("Note", backref="labels", lazy="dynamic")


@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")


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
                next = url_for("login")
            return redirect(next)
    return render_template("login.html", form=form)


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))


@app.route("/note", methods=["GET", "POST"])
@login_required
def note():
    """
        Displays current users notes
    """
    notes = current_user.notes
    return render_template("note.html", notes=notes)


@app.route("/add_note", methods=["GET", "POST"])
@login_required
def add_note():
    """
        Creates notes. Label must be created before note.
    """
    form = NoteForm()
    form.label.choices = [(g.name) for g in current_user.labels]
    if form.validate_on_submit():
        note = Note(
            title=form.title.data,
            content=form.content.data,
            label_id=form.label.data,
            author_id=current_user.id,
        )
        db.session.add(note)
        db.session.commit()
        return redirect(url_for("note"))
    return render_template("add_note.html", form=form)


@app.route("/label", methods=["GET", "POST"])
@login_required
def label():
    """
        Creates labels.
    """
    labels = current_user.labels
    form = LabelForm()
    if form.validate_on_submit():
        label = Label(name=form.label.data, author_id=current_user.id)
        db.session.add(label)
        db.session.commit()
        return redirect(url_for("label"))
    return render_template("label.html", form=form, labels=labels)


@app.route("/delete/note/<int:id>", methods=["GET", "POST"])
@login_required
def delete_note(id):
    """
        Deletes note from database.
    """
    note = Note.query.get_or_404(id)
    db.session.delete(note)
    db.session.commit()
    return redirect(url_for("note"))


@app.route("/delete/label/<int:id>", methods=["GET", "POST"])
@login_required
def delete_label(id):
    """
        Deletes label from database.
    """
    label_name = Label.query.get_or_404(id)
    db.session.delete(label_name)
    db.session.commit()
    return redirect(url_for("label"))


@app.route("/edit_label/<int:id>", methods=["GET", "POST"])
@login_required
def edit_label(id):
    """
        Updates label name.
    """
    form = EditLabelForm()
    if form.validate_on_submit():
        label = Label.query.get_or_404(id)
        label.name = form.label.data
        db.session.commit()
        return redirect(url_for("label"))
    return render_template("edit_label.html", form=form)


@app.route("/edit_note/<int:id>", methods=["GET", "POST"])
@login_required
def edit_note(id):
    """
        Updates note title, content.
    """
    form = EditNoteForm()
    if form.validate_on_submit():
        note = Note.query.get_or_404(id)
        note.title = form.title.data
        note.content = form.content.data
        db.session.commit()
        return redirect(url_for("note"))
    return render_template("edit_note.html", form=form)


@app.route("/search", methods=["GET", "POST"])
def search():
    """
        Displays result of search in current users notes.
    """
    form = SearchForm()
    title = request.args.get("title")
    if title:
        notes = current_user.notes.filter(Note.title.contains(title))
        return render_template("search.html", form=form, notes=notes)
    return render_template("search.html", form=form)


@app.route("/filter", methods=["GET", "POST"])
def filter():
    """
        Displays current users notes filtered by label name.
    """
    form = FilterForm()
    form.label.choices = [(g.name) for g in current_user.labels]
    label = request.args.get("label")
    if label:
        notes = current_user.notes.filter(Note.title.contains(label))
        return render_template("search.html", form=form, notes=notes)
    return render_template("search.html", form=form)
