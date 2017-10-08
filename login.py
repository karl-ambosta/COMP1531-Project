from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtform import StrignField, PasswordField, BooleanField
from wtforms.validatiors import InputRequired

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Secretkey!'
Bootstrap(app)

class LoginForm(FlaskForm):
    username = StringField('username', validators=[InputRequired()])
    password = PasswordField('password', validators=[InputRequired()])

class RegisterForm(FlaskForm):
    username = StringField('username', validators=[InputRequired()])
