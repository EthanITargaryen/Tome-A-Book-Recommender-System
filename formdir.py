from flask_wtf import FlaskForm
from wtforms import *
from wtforms.validators import *


class LoginForm(FlaskForm):
    us = StringField("Username", validators=[DataRequired()])
    pw = StringField("Password", validators=[DataRequired()])
    sub = SubmitField("Submit")


class EvaluationForm(FlaskForm):
    rating = SelectField("Rating", choices=[1, 2, 3, 4, 5], validators=[DataRequired()])
    review = TextAreaField("Review")
    submit = SubmitField("Submit")


class AdminAuthorForm(FlaskForm):
    # PERSON_ID, FULL_NAME, DATE_OF_BIRTH, HOMETOWN, IMAGE_URL, GENDER, AUTHOR_ID, ABOUT, WEBPAGE
    full_name = StringField("Full Name", validators=[DataRequired(message='Must not be empty')])
    dob = StringField("Date of Birth", validators=[DataRequired(message='Must be a valid date')])
    hometown = StringField("Hometown", validators=[DataRequired(message='Must not be empty')])
    image_url = StringField("Image URL", validators=[URL(), DataRequired(message='Must be a valid URL')])
    gender = SelectField("Gender", choices=['Male', 'Female', 'Prefer not to say'])
    about = TextAreaField("About", validators=[DataRequired(message='Must not be empty')])
    webpage = StringField("Webpage", validators=[URL()])
    submit = SubmitField("Submit")


class AdminBookForm(FlaskForm):
    # authors, genres, TITLE, PUBLICATION_DATE, ISBN
    # , LANGUAGE, NUM_PAGES, IMAGE_URL, DESCRIPTION, PUBLISHER_NAME, COUNTRY
    title = StringField("Title", validators=[DataRequired()])
    authors = StringField("Authors\n(In Comma Seperated Format)", validators=[DataRequired()])
    genres = StringField("Genres\n(In Comma Seperated Format)", validators=[DataRequired()])
    publisher = StringField("Publishing House")
    pub_date = StringField("Publication Date")
    country = StringField("Country")
    isbn = IntegerField("ISBN")
    language = StringField("Language")
    num_pages = IntegerField("Number of Pages")
    image_url = StringField("Image URL", validators=[DataRequired()])
    description = TextAreaField("Description", validators=[DataRequired()])

