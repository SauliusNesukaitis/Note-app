from wtforms.validators import DataRequired, Length, Regexp, EqualTo
from flask_wtf import FlaskForm
from wtforms import (
    SubmitField,
    StringField,
    BooleanField,
    PasswordField,
    ValidationError,
    SelectField,
)


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(1, 64)])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Keep me logged in")
    submit = SubmitField("Log in")


class RegistrationForm(FlaskForm):
    username = StringField(
        "Username",
        validators=[
            DataRequired(),
            Length(1, 64),
            Regexp(
                "^[A-Za-z0-9][A-Za-z0-9_.]*$",
                0,
                "Usernames must have only letters, numbers, dots or underscores"
            ),
        ],
    )
    password = PasswordField(
        "Password",
        validators=[
            DataRequired(),
            EqualTo("password2", message="Passwords must match."),
        ],
    )
    password2 = PasswordField("Confirm password", validators=[DataRequired()])
    submit = SubmitField("Register")


class NoteForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired(), Length(1, 16)])
    content = StringField("Content", validators=[DataRequired(), Length(1, 64)])
    label = SelectField('Label')
    submit = SubmitField("Add")


class LabelForm(FlaskForm):
    label = StringField("Label name", validators=[DataRequired(), Length(1, 16)])
    submit = SubmitField("Add")


class EditLabelForm(FlaskForm):
    label = StringField("Label name", validators=[DataRequired(), Length(1, 16)])
    submit = SubmitField("Update label")


class EditNoteForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired(), Length(1, 16)])
    content = StringField("Content", validators=[DataRequired(), Length(1, 64)])
    submit = SubmitField("Update note")