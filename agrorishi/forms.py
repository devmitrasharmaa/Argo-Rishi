import datetime
from flask_login import current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileField,FileAllowed
from wtforms import BooleanField, DateField, IntegerField, SelectField, StringField, PasswordField,SubmitField, TextAreaField, ValidationError
from wtforms.validators import DataRequired, Length, Email ,EqualTo, Optional,InputRequired
from flask_login import current_user
from datetime import date
from .models import Farmers, PostCategory

class RegistrationForm(FlaskForm):
    username= StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email=StringField('Email', 
                      validators=[DataRequired(), Email()])
    password= PasswordField('Password',
                            validators=[DataRequired()])
    confirm_password= PasswordField('Confirm Password',
                            validators=[DataRequired(), EqualTo('password')])
    submit= SubmitField('Sign Up')

    def validate_username(self,username):
        faculty = Farmers.query.filter_by(username=username.data).first()
        if faculty:
            raise ValidationError('This username is already Taken, try another username')
        
    def validate_email(self,email):
        faculty = Farmers.query.filter_by(email=email.data).first()
        if faculty:
            raise ValidationError('This email is already in use, try to log in')

class LoginForm(FlaskForm):
    email=StringField('Email', 
                      validators=[DataRequired(), Email()])
    password= PasswordField('Password',
                            validators=[DataRequired()])
    submit= SubmitField('Login')
    remember=BooleanField('Remember')

class UpdateAccountForm(FlaskForm):
    username = StringField('Username', 
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', 
                        validators=[DataRequired(), Email()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    class_ = SelectField('Add Class', choices=[], validators=[Optional()])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = Farmers.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = Farmers.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')

class PostForm(FlaskForm):
    picture = FileField('Image', validators=[DataRequired()])
    caption = StringField('Caption', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[Optional()])
    category = SelectField('Category', choices=[(category.name, category.value) for category in PostCategory], validators=[DataRequired()])
    submit = SubmitField('Post')

