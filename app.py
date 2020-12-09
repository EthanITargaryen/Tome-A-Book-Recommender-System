from flask import Flask, render_template, flash, request, g, redirect, url_for, session
from flask_bootstrap import Bootstrap
from flask_mail import Mail, Message
from flask_login import UserMixin, LoginManager, login_required, login_user, logout_user
from flask_bcrypt import Bcrypt
from functools import wraps
import numpy as np
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
app.config['DB_PASSWORD'] = "Ne$qDrbwAYpp"  # os.environ.get('DB_PASSWORD')
app.config['BRS_MAIL_SUBJECT_PREFIX'] = '[BRS]'
app.config['BRS_MAIL_SENDER'] = 'BRS Admin ' + app.config['DB_EMAIL']
app.config['SESSION'] = session

app.secret_key = b'_5#y1L"FR8z\n\xec]/'

bootstrap = Bootstrap(app)
mail = Mail(app)
bcrypt = Bcrypt(app)
global recommender


def my_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('username') or None:
            return f(*args, **kwargs)
        else:
            flash("You should be logged in!")
            return redirect(url_for('login', next=request.url))

    return decorated_function


def admin_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('admin_privileges') or None:
            return f(*args, **kwargs)
        else:
            flash("You should be logged in!")
            return redirect(url_for('login', next=request.url))

    return decorated_function


def render_my_template(html, **kwargs):
    return render_template(html, id=session.get('id'), s_username=session.get('username'),
                           admin_privileges=session.get('admin_privileges', False) ,**kwargs)


''' RANDOM UTILITIES'''


@app.route('/com')
def com():
    return render_template('comment_temp.html')


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
            flash("Login Successful, " + username)
            return redirect(url_for('m_about'))
    return render_my_template('clib/login.html')


@app.route('/administrator_login', methods=['GET', 'POST'])
def administrator_login():
    if session.get('username') or None:
        return redirect(url_for('m_about'))
    if request.method == 'POST':
        username = request.form.get('your_name')
        password = request.form.get('your_pass')
        r_id = check_username_password(username, password)
        if r_id is None:
            flash("Invalid Username/Password")
        elif r_id != 6926:
            flash("Insufficient Privileges")
        else:
            session['username'] = username
            session['id'] = r_id
            session['admin_privileges'] = True
            flash("Welcome, admin!!!")
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
                return render_my_template('author.html', name="R Tagore",
                                          image="https://images.gr-assets.com/authors/1453892068p7/36913.jpg",
                                          about="Hi, ewfferiahjghjrehehjhnjrdfghsfsjghsjhjrghrj eghuewhgew bfhweb urbg uewgb ueb whbg ewhb uewb guerwbgewyhb feru vbyf bvewuf vrye eryb eug ewu uewbv uewb gueiq")

    return render_my_template('clib/register.html')


@app.route('/', methods=['GET', 'POST'])
def m_about():
    global recommender
    if request.method == 'GET':
        if 'recommender' not in globals():
            print('Not in globals')
            recommender = MyRecommender()
        return render_my_template('home.html')
    else:
        key = request.form.get('Search')
        return redirect(url_for('search_with_key', key=key))


@app.route('/wert')
def wert():
    global recommender
    print(recommender.list_recommended_books(7105))
    return 'High in the halls!'


@app.route('/author/<brs_id>')
def author(brs_id):
    try:
        if str(brs_id).isnumeric() or str(brs_id)[1:].isnumeric():
            ret = info_for_author_id(brs_id)
        else:
            ret = info_for_author_name(brs_id)
        print(ret)
        books = []
        for b_id in ret['book']:
            b_ret = info_for_book_id(b_id)
            print(b_ret.get('book_id'))
            books.append(tuple((b_ret.get('title'), b_ret.get('image'), b_ret.get('book_id'))))
        print(books)
        fol = check_follow(session.get('id'), brs_id)
        if ret is not None:
            return render_my_template("author.html", books=books, author_id=ret['author_id']
                                      , gender=ret['gender'], hometown=ret['hometown'], dob=ret['dob']
                                      , follow = fol, no_books=ret['no_books'], name=ret['name']
                                      , about=ret['about'], image=ret['image'], fol=ret['fol']
                                      , skipbar=False)
    except Exception as e:
        return str(e)
    return "BRS!"


@app.route('/reader/<brs_id>')
def reader(brs_id, is_self=False):
    try:
        if str(brs_id).isnumeric() or str(brs_id)[1:].isnumeric():
            ret = info_for_reader_id(brs_id)
        elif str(brs_id).lower() == 'admin':
            return "ERROR 404 NOT FOUND"
        else:
            ret = info_for_username(brs_id)
            if ret is None:
                ret = info_for_full_name(brs_id)
        print(ret)
        books = []
        for b_id in ret['book']:
            b_ret = info_for_book_id(b_id)
            # print(b_ret.get('book_id'))
            books.append(tuple((b_ret.get('title'), b_ret.get('image'), b_ret.get('book_id'))))
        print(books)
        is_self = (session.get('id') == brs_id)
        evals = []
        for eval_id in ret['eval']:
            eval_ret = info_for_eval_id(eval_id)
            evals.append(tuple((eval_ret.get('title'), eval_ret.get('image'), eval_ret.get('book_id'),
                                eval_ret.get('rating'), eval_ret.get('review'))))
        if ret is not None:
            return render_my_template("reader.html", evals=evals, books=books, is_this_self=is_self, **ret)
    except Exception as e:
        return str(e)
    return "BRS!"


@app.route('/genre/<brs_id>')
def genre(brs_id):
    try:
        ret = books_of_a_genre(brs_id)
        books = []
        for b_id in ret['book']:
            b_ret = info_for_book_id(b_id)
            # print(b_ret.get('book_id'))
            books.append(tuple((b_ret.get('title'), b_ret.get('image'), b_ret.get('book_id'))))
        print(books)
        return render_my_template('genre.html', name=brs_id, books=books)
    except Exception as e:
        return str(e)
    return "BRS!"


@app.route('/language/<brs_id>')
def language(brs_id):
    try:
        ret = books_of_a_language(brs_id)
        books = []
        for b_id in ret['book']:
            b_ret = info_for_book_id(b_id)
            print(b_ret.get('book_id'))
            books.append(tuple((b_ret.get('title'), b_ret.get('image'), b_ret.get('book_id'))))
        print(books)
        return render_my_template('genre.html', name=brs_id, books=books)
    except Exception as e:
        return str(e)
    return "BRS!"


@app.route('/publisher/<brs_id>')
def publisher(brs_id):
    try:
        ret = books_of_a_publisher(brs_id)
        books = []
        for b_id in ret['book']:
            b_ret = info_for_book_id(b_id)
            print(b_ret.get('book_id'))
            books.append(tuple((b_ret.get('title'), b_ret.get('image'), b_ret.get('book_id'))))
        print(books)
        return render_my_template('genre.html', name=brs_id, books=books)
    except Exception as e:
        return str(e)
    return "BRS!"


@app.route('/book/<brs_id>')
def book(brs_id):
    try:
        if str(brs_id).isnumeric() or str(brs_id)[1:].isnumeric():
            ret = info_for_book_id(brs_id)
        else:
            ret = info_for_book_title(brs_id)
        author_names = []
        for author_id in ret['author']:
            author_names += [info_for_author_id(author_id)['name']]
        print(ret)
        evals = []
        for eval_id in ret['eval']:
            eval_ret = info_reader_for_eval_id(eval_id)
            evals.append(tuple((eval_ret.get('full_name'), eval_ret.get('image'), eval_ret.get('reader_id'),
                                eval_ret.get('rating'), eval_ret.get('review'), eval_ret.get('date'))))

        if session.get('id'):
            ret['eval'] = check_wish_read_or_eval(session.get('id'), brs_id, 'e')
            ret['read'] = check_wish_read_or_eval(session.get('id'), brs_id, 'r')
            ret['wish'] = check_wish_read_or_eval(session.get('id'), brs_id, 'w')
            ret['read'] |= ret['eval']
            ret['wish'] |= ret['read']
        if ret is not None:
            return render_my_template('book.html', evals=evals
                                      , author_names=author_names, **ret)
    except Exception as e:
        return str(e)
    return 'Brs!'


@app.route('/genres')
def all_genres():
    ag = find_all_genres()
    return render_my_template('all_base.html', fields=ag, type='genre', page_title = 'All Genres')


@app.route('/authors')
def all_authors():
    ag = find_all_authors()
    return render_my_template('all_base.html', fields=ag, type='author', page_title = 'All Authors')


@app.route('/languages')
def all_languages():
    ag = find_all_languages()
    return render_my_template('all_base.html', fields=ag, type='language', page_title = 'All Languages')


@app.route('/publishers')
def all_publishers():
    ag = find_all_publishers()
    return render_my_template('all_base.html', fields=ag, type='publisher', page_title = 'All Publishers')


@app.route('/index')
def ad_index():
    return render_template('admin/index.html')


@app.route('/search/<key>', methods=['GET', 'POST'])
def search_with_key(key):
    if request.method == 'GET':
        ret = substr_search(key)
        return render_my_template('search.html', **ret)
    else:
        key = request.form.get('Search')
        ret = substr_search(key)
        return render_my_template('search.html', **ret)


# New Add here
@app.route('/follow_author/<a_id>')
@my_login_required
def follows(a_id):
    if follow_an_author(a_id, session.get('id')):
        flash("You are already following the author")
    return redirect(url_for("author", brs_id=a_id))


@app.route('/wishes/<b_id>')
@my_login_required
def wishes(b_id):
    if not wish_or_read(session.get('id'), b_id, 'w'):
        flash('You prolly already selected this option')
    return redirect(url_for("book", brs_id=b_id))


@app.route('/reads/<b_id>')
@my_login_required
def reads(b_id):
    if not wish_or_read(session.get('id'), b_id, 'r'):
        flash('You prolly already selected this option')
    return redirect(url_for("book", brs_id=b_id))


@app.route('/eval/<b_id>')
@my_login_required
def evals(b_id):
    if not wish_or_read(session.get('id'), b_id, 'e'):
        flash('You prolly already selected this option')
        return redirect(url_for("book", brs_id=b_id))
    else:
        return "{% extends base.html %} \n Under construction "


@app.route('/evaluate/<b_id>', methods=['GET', 'POST'])
@my_login_required
def evaluated(b_id):
    global recommender
    try:
        if str(b_id).isnumeric():
            ret = info_for_book_id(b_id)
        else:
            ret = info_for_book_title(b_id)
        b_id = ret['book_id']
        title = ret['title']
        image = ret['image']
        form = formdir.EvaluationForm()
        if request.method == 'POST':
            if form.validate_on_submit():
                x = form.rating.data
                y = form.review.data
                print("x: ", x)
                print("y: ", y)
                if insert_evaluation(session.get('id'), b_id, x, y) or None:
                    try:
                        if recommender:
                            x_update = pd.DataFrame({
                                'user_id': [int(session.get('id'))], 'item_id': [int(b_id)]
                            })
                            y_update = np.array([int(x)])
                            recommender.matrix_fact.update_users(
                                x_update, y_update, lr=0.001, n_epochs=20, verbose=0
                            )
                            print('Recommender should be updated.')
                    except Exception as e:
                        print('Recommender has not been updated. Error:', e)
                    flash("Evaluation Done!")
                    return redirect(url_for('book', brs_id=b_id))
                else:
                    flash("Something went wrong!")
        return render_my_template('eval.html', form=form, title=title, image=image)
    except Exception as e:
        return str(e)
    return 'Brs!'


@app.route('/recommend')
@my_login_required
def recommend_me():
    global recommender
    ret = recommender.list_recommended_books(session.get('id'))
    books = []
    for b_id in ret:
        b_ret = info_for_book_id(b_id)
        # print(b_ret.get('book_id'))
        books.append(tuple((b_ret.get('title'), b_ret.get('image'), b_ret.get('book_id'))))
    print(books)
    return render_my_template('genre.html', name='Recommendation for ' + str(session.get('username')), books=books)


@app.route('/following')
@my_login_required
def following_authors():
    try:
        ret = authors_following(session.get('id'))
        authors = []
        for a_id in ret['fols']:
            a_ret = info_for_author_id(a_id)
            authors.append(tuple((a_ret.get('name'), a_ret.get('image'), a_ret.get('author_id'))))
        return render_my_template('genre.html', follow_authors=True, books=authors)
    except Exception as e:
        return str(e)


@app.route('/comment/<brs_id>', methods=['GET', 'POST'])
@my_login_required
def comment_on_book(brs_id):
    x = brs_id
    try:
        print("Request form keys:")
        for k in request.form.keys():
            print(k, request.form.get(k), end=' ')

        print('\nInit ', end='')
        print("BRS: ", brs_id)
        if request.method == 'POST':
            print("Second BRS:", brs_id )
            if request.form.get('comment'):
                text = request.form.get('comment')
                if insert_comment(text, brs_id, session.get('id')):
                    print("Inserted, text")
            elif request.form.get('reply'):
                text = request.form.get('reply')
                if insert_comment(text, brs_id, session.get('id'), par_id=request.form.get('c_id')):
                    print("Inserted, text")
            print("Third BRS:", x)
            # return redirect(url_for('comment_on_book', brs_id=x))
        print("BRS: ", brs_id)
        ret = comments_for_book_id(brs_id)
        print(ret)
        return render_my_template('comment_temp.html', **ret)
    except Exception as e:
        return str(e)


@app.route('/self')
@my_login_required
def self_name():
    return str(session.get('username'))


@app.route('/change_password', methods=['GET', 'POST'])
@my_login_required
def pw_change():
    form = formdir.PasswordUpdateForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            if update_password(session.get('username'), form.old_password.data, form.new_password.data):
                flash("Password updated successfully!")
                return redirect(url_for('reader', brs_id=session.get('id')))
            else:
                flash("Password was not updated.")
    return render_my_template('pwupdate.html', form=form)


@app.route('/signout')
@my_login_required
def sign_out():
    session.pop('username')
    session.pop('id')
    session.pop('admin_privileges', 0)
    flash('Signed Out')
    return redirect(url_for('m_about'))


@app.route('/admin_home')
@admin_login_required
def admin_home():
    flash("HELLO, ADMIN")
    return render_my_template('base.html')


@app.route('/adminstrator_add_author', methods=['GET', 'POST'])
@admin_login_required
def admin_add_author():
    try:
        form = formdir.AdminAuthorForm()
        print(form.is_submitted())
        if form.validate_on_submit():
            # ret = dict(form)
            # print(ret)
            if admin_add_author_db(form.full_name.data, form.dob.data, form.hometown.data,
                                   form.image_url.data, form.gender.data, form.about.data, form.webpage.data):
                flash("Author " + form.full_name.data + " has successfully been inserted!")
                return redirect(url_for('admin_home'))
        return render_my_template('admin_author_form.html', form=form)
    except Exception as e:
        return str(e)


@app.route('/adminstrator_add_book', methods=['GET', 'POST'])
@admin_login_required
def admin_add_book():
    try:
        form = formdir.AdminBookForm()
        if form.validate_on_submit():
            if admin_add_book_db(form.authors.data, form.genres.data, form.title.data, form.pub_date.data,
                                 form.isbn.data, form.language.data, form.num_pages.data, form.image_url.data,
                                 form.description.data, form.publisher.data, form.country.data):
                flash("Book " + form.title.data + " has successfully been inserted!")
                print("Insertion done!")
                return redirect(url_for('admin_home'))
            else:
                flash("An error occurred")
        return render_my_template('admin_book_form.html', form=form)
    except Exception as e:
        return str(e)


if __name__ == '__main__':
    app.run()
