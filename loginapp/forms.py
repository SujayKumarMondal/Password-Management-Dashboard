import re
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
import regex
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms import validators
import wtforms
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from loginapp.models import User
from wtforms.validators import DataRequired, Length, Email, EqualTo, Regexp


def password_validator(form, field):
    """ Custom password validator to enforce password rules. """
    password = field.data
    # Minimum 6 characters, maximum 20 characters
    if len(password) < 6 or len(password) > 20:
        raise ValidationError("Password must be between 6 and 20 characters.")

    # Must contain at least one number
    if not re.search(r'\d', password):
        raise ValidationError("Password must contain at least one number.")

    # Must contain at least one special character (excluding restricted ones)
    if not re.search(r'[!@#$%^&*()_+={}[\]:;"\'<>,.?\\|`~]', password):
        raise ValidationError("Password must contain at least one special character.")

    # Must not contain `_`, `/`, or `,`
    if re.search(r'[_/\,]', password):
        raise ValidationError("Password cannot contain '_', '/', or ','.")

class RegistrationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=6, max=20),
        Regexp(r'^(?!.*[_,/]).*$', message="Password cannot contain _, / or ,"),  # Disallow _, /, and ,
        Regexp(r'.*[A-Za-z].*', message="Password must contain at least one letter"),
        Regexp(r'.*\d.*', message="Password must contain at least one number"),
        Regexp(r'.*[\W_].*', message="Password must contain at least one special character"),  # Special character
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message="Passwords must match")
    ])
    submit_btn = SubmitField('Sign Up')

    # Adding validation for abnormal anomalies
    def validate_email(self, email):
        test_condition = User.query.filter_by(email=email.data).first()
        if test_condition:
            raise ValidationError('Email already exists in the database.')

class LoginForm(FlaskForm):    
    """
    Login form 
    Elements containing:
    1. email
    2. password
    3. submit button
    """
    email = StringField('Email', validators=[DataRequired(), Email()])

    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember me')
    submit_btn = SubmitField('Login')


class AddPassword(FlaskForm):
    """ Form for add page. Where user will input their credential in password manager. """
    webaddress = StringField('Web Address', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=6, max=20),
        Regexp(r'^(?!.*[_,/]).*$', message="Password cannot contain _, / or ,"),
        Regexp(r'.*[A-Za-z].*', message="Password must contain at least one letter"),
        Regexp(r'.*\d.*', message="Password must contain at least one number"),
        Regexp(r'.*[\W_].*', message="Password must contain at least one special character"),
    ])

    submit_btn = SubmitField('Submit')

# password reset form
class RequestResetForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit_btn = SubmitField('Request Password Reset')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('There is no account with this email. You must register first.')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired(), password_validator])
    confirm_password = PasswordField('Confirm password', validators=[DataRequired(), EqualTo('password')])

    submit_btn = SubmitField('Reset Password')


class UserAccountUpdate(FlaskForm):    
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit_btn = SubmitField('Update')

    # Adding validation for abnormal anomalies
    def validate_email(self, email):
        if email.data != current_user.email:
            test_condition = User.query.filter_by(email=email.data).first()
            if test_condition:
                raise ValidationError('Email already exists in the database.')

class UpdatePassword(FlaskForm):
    webaddress = StringField('Website Address', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=6, max=20),
        Regexp(r'^(?!.*[_,/]).*$', message="Password cannot contain _, / or ,"),
        Regexp(r'.*[A-Za-z].*', message="Password must contain at least one letter"),
        Regexp(r'.*\d.*', message="Password must contain at least one number"),
        Regexp(r'.*[\W_].*', message="Password must contain at least one special character"),
    ])
    submit_btn = SubmitField('Update Password')
