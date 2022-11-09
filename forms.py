from wtforms import SubmitField, StringField, BooleanField, PasswordField, ValidationError
from wtforms.validators import DataRequired, Length, Regexp, EqualTo
from flask_wtf import FlaskForm

class LoginForm(FlaskForm):
    username = StringField(
        "Username", validators=[DataRequired(), Length(1, 64)]
    )
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