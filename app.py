from flask import Flask, render_template, flash, request, g, redirect, url_for, session
from flask_bootstrap import Bootstrap
from flask_mail import Mail, Message
from flask_login import UserMixin, LoginManager, login_required, login_user, logout_user
from functools import wraps
import cx_Oracle as cx
import os
import formdir
from dbutils import *
from dbutils2 import *
from urllib.parse import urlparse, urljoin


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc

"""
    #c3e6cb
    1 ... EVALUATION PRIVILEGE 
"""

app = Flask(__name__)
app.config['SECRET_KEY'] = 'HighInTheHalls'
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['DB_EMAIL'] = os.environ.get('MAIL_USERNAME')
app.config['DB_PASSWORD'] = "Ne$qDrbwAYpp" # os.environ.get('DB_PASSWORD')
app.config['BRS_MAIL_SUBJECT_PREFIX'] = '[BRS]'
app.config['BRS_MAIL_SENDER'] = 'BRS Admin ' + app.config['DB_EMAIL']
app.config['SESSION'] = session

app.secret_key = b'_5#y1L"FR8z\n\xec]/'

bootstrap = Bootstrap(app)
mail = Mail(app)


def my_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('username') or None:
            return f(*args, **kwargs)
        else:
            flash("You should be logged in!")
            return redirect(url_for('login', next=request.url))
    return decorated_function


def render_my_template(html, **kwargs):
    return render_template(html, id = session.get('id'), **kwargs)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('username') or None:
        return redirect(url_for('m_about'))
    if request.method == 'POST':
        username = request.form.get('your_name')
        password = request.form.get('your_pass')
        r_id = check_username_password(username, password)
        if r_id is None:
            flash("Invalid Username/Password")
        else:
            session['username'] = username
            session['id'] = r_id
            return redirect(url_for('m_about'))
    return render_my_template('clib/login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        if request.form.get('pass') != request.form.get('re_pass'):
            flash("Passwords do not match")
        else:
            for u, v in request.form.items():
                print(u, v)
            if not register_into_db(fullname=request.form.get("fname"), email=request.form.get('email')
                             , password=request.form.get('pass'), hometown=request.form.get('ht')
                             , dob=request.form.get('dob'), image=request.form.get('iurl')
                             , gender=request.form.get('exampleRadios'), username=request.form.get('uname')):
                flash("Something went wrong. Register again.")
            else:
                return render_my_template('author.html', name="R Tagore", image="https://images.gr-assets.com/authors/1453892068p7/36913.jpg", about="Hi, ewfferiahjghjrehehjhnjrdfghsfsjghsjhjrghrj eghuewhgew bfhweb urbg uewgb ueb whbg ewhb uewb guerwbgewyhb feru vbyf bvewuf vrye eryb eug ewu uewbv uewb gueiq")

    return render_my_template('clib/register.html')


@app.route('/')
def m_about():
    print("It comes here")
    return render_my_template('author.html', name="R Tagore"
                              , image="https://images.gr-assets.com/authors/1453892068p7/36913.jpg"
                              , about="Hi, ewfferiahjghjrehehjhnjrdfghsfsjghsjhjrghrj eghuewhgew bfhweb urbg uewgb ueb whbg ewhb uewb guerwbgewyhb feru vbyf bvewuf vrye eryb eug ewu uewbv uewb gueiq")


@app.route('/author/<id>')
def author(id):
    try:
        if str(id).isnumeric():
            ret = info_for_author_id(id)
        else:
            ret = info_for_author_name(id)
        print(ret)
        books = []
        for b_id in ret['book']:
            b_ret = info_for_book_id(b_id)
            print(b_ret.get('book_id'))
            books.append(tuple((b_ret.get('title'), b_ret.get('image'), b_ret.get('book_id'))))
        print(books)
        if ret is not None:
            return render_my_template("author.html", books=books, author_id = ret['author_id'], gender = ret['gender']
                        , hometown = ret['hometown'], dob = ret['dob']
                        , name = ret['name'], about = ret['about'], image = ret['image'], skipbar = False)
    except Exception as e:
        return str(e)
    return "BRS!"


@app.route('/reader/<id>')
def reader(id):
    try:
        if str(id).isnumeric():
            ret = info_for_reader_id(id)
        else:
            ret = info_for_username(id)
        print(ret)
        books = []
        for b_id in ret['book']:
            b_ret = info_for_book_id(b_id)
            print(b_ret.get('book_id'))
            books.append(tuple((b_ret.get('title'), b_ret.get('image'), b_ret.get('book_id'))))
        print(books)
        if ret is not None:
            return render_my_template("reader.html", books=books, **ret)
    except Exception as e:
        return str(e)
    return "BRS!"


@app.route('/genre/<name>')
def genre(name):
    try:
        ret = books_of_a_genre(name)
        books = []
        for b_id in ret['book']:
            b_ret = info_for_book_id(b_id)
            print(b_ret.get('book_id'))
            books.append(tuple((b_ret.get('title'), b_ret.get('image'), b_ret.get('book_id'))))
        print(books)
        return render_my_template('genre.html', name = name, books=books)
    except Exception as e:
        return str(e)
    return "BRS!"


@app.route('/book/<b_id>')
def book(b_id):
    try:
        if str(b_id).isnumeric():
            ret = info_for_book_id(b_id)
        else:
            ret = info_for_book_title(b_id)
        author_names = []
        for author_id in ret['author']:
            author_names += [info_for_author_id(author_id)['name']]
        print(ret)
        if session.get('id'):
            ret['eval'] = check_wish_read_or_eval(session.get('id'), b_id, 'e')
            ret['read'] = check_wish_read_or_eval(session.get('id'), b_id, 'r')
            ret['wish'] = check_wish_read_or_eval(session.get('id'), b_id, 'w')
            ret['read'] |= ret['eval']
            ret['wish'] |= ret['read']
        if ret is not None:
            return render_my_template('book.html', author_names = author_names, **ret)
    except Exception as e:
        return str(e)
    return 'Brs!'


@app.route('/wishes/<b_id>')
@my_login_required
def wishes(b_id):
    if not wish_or_read(session.get('id'), b_id, 'w'):
        flash('You prolly already selected this option')
    return redirect(url_for("book", b_id=b_id))


@app.route('/reads/<b_id>')
@my_login_required
def reads(b_id):
    if not wish_or_read(session.get('id'), b_id, 'r'):
        flash('You prolly already selected this option')
    return redirect(url_for("book", b_id=b_id))


@app.route('/eval/<b_id>')
@my_login_required
def evals(b_id):
    if not wish_or_read(session.get('id'), b_id, 'e'):
        flash('You prolly already selected this option')
        return redirect(url_for("book", b_id=b_id))
    else:
        return "{% extends base.html %} \n Under construction "


@app.route('/evaluate/<b_id>', methods=['GET', 'POST'])
@my_login_required
def evaluated(b_id):
    try:
        if str(b_id).isnumeric():
            ret = info_for_book_id(b_id)
        else:
            ret = info_for_book_title(b_id)
        b_id = ret['book_id']
        title = ret['title']
        form = formdir.EvaluationForm()
        if request.method == 'POST':
            if form.validate_on_submit():
                x = form.rating.data
                y = form.review.data
                print("x: ", x)
                print("y: ", y)
                if insert_evaluation(session.get('id'), b_id, x, y) or None:
                    flash("Evaluation Done!")
                    return redirect(url_for('book', b_id=b_id))
                else:
                    flash("Something went wrong!")
        return render_my_template('eval.html', form=form, title=title)
    except Exception as e:
        return str(e)
    return 'Brs!'


@app.route('/self')
@my_login_required
def self_name():
    return str(session.get('username'))


@app.route('/signout')
@my_login_required
def sign_out():
    session.pop('username')
    session.pop('id')
    return redirect(url_for('m_about'))


if __name__ == '__main__':
    app.run()
