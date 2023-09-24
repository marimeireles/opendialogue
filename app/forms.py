from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
    BooleanField,
    TextAreaField,
    SubmitField,
    DateTimeField,
    IntegerField,
)
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length, Regexp
from wtforms.fields import DateField, TimeField
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import NumberRange, DataRequired

from app.models import User


class EventForm(FlaskForm):
    name = StringField("Event Name", validators=[DataRequired()])
    description = TextAreaField("Event Description", validators=[DataRequired()])
    location = StringField("Event Location", validators=[DataRequired()])
    date = DateField("Event Date", format='%Y-%m-%d', validators=[DataRequired()])
    time = TimeField("Event Time", format='%H:%M', validators=[DataRequired()])
    image = FileField('Image', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    require_approval = BooleanField('Require Approval for RSVP')
    max_attendees = IntegerField('Max Attendees', validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField('Create Event')

def strong_password(form, field):
    password = field.data
    if len(password) < 8:
        raise ValidationError("Password must be at least 8 characters long")
    if not any(char.isupper() for char in password):
        raise ValidationError("Password must contain at least one uppercase letter")
    if not any(char.islower() for char in password):
        raise ValidationError("Password must contain at least one lowercase letter")
    if not any(char.isdigit() for char in password):
        raise ValidationError("Password must contain at least one digit")


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Remember me")
    submit = SubmitField("Sign in")


class RegistrationForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired(), strong_password])
    password2 = PasswordField("Repeat Password", validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("Register")

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError("Please use a different username.")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError("Please use a different email address.")


class EditProfileForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    about_me = TextAreaField("About me", validators=[Length(min=0, max=140)])
    submit = SubmitField("Submit")

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError("Please use a different username.")


class PostForm(FlaskForm):
    post = TextAreaField("Say something", validators=[DataRequired(), Length(min=1, max=140)])
    submit = SubmitField("Submit")


class ResetPasswordRequestForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    submit = SubmitField("Request Password Reset")


class ResetPasswordForm(FlaskForm):
    password = PasswordField("Password", validators=[DataRequired()])
    password2 = PasswordField("Repeat Password", validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("Request Password Reset")
