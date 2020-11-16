from flask_wtf import  FlaskForm
from wtforms import *
from wtforms.validators import DataRequired, NumberRange


class LoginForm(FlaskForm):
    us = StringField("Username", validators=[DataRequired()])
    pw = StringField("Password", validators=[DataRequired()])
    sub = SubmitField("Submit")


class EvaluationForm(FlaskForm):
    rating = SelectField("Rating", choices=[1, 2, 3, 4, 5], validators=[DataRequired()])
    review = TextAreaField("Review")
    submit = SubmitField("Submit")
