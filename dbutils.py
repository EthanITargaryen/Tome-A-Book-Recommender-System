import cx_Oracle as cx
import time
import pandas as pd
from matrix_factorization import *

""""
with cx.connect('ZOIN', 'ZOIN', dsn=cx.makedsn('localhost', 1521, None, 'ORCL'),
                        encoding="UTF-8") as con:            
                        """


def db_log_print(text, **kwargs):
    with open('db_log.txt', 'a', encoding='UTF-8') as file:
        print("\n", file=file)
        print(time.asctime(), file=file)
        print(text, kwargs, file=file)


def username_password_check(username, password):
    flag = None
    try:
        with cx.connect('ZOIN', 'ZOIN', dsn=cx.makedsn('localhost', 1521, None, 'ORCL'),
                        encoding="UTF-8") as con:
            cur = con.cursor()
            print(password, hash(password))
            for row in cur.execute("SELECT READER_ID FROM READER WHERE USERNAME = :1 AND PASSWORD_HASH IN (:2, :3)",
                        [username, password, str(hash(password))]):
                print(password, hash(password))
                flag = row[0]
    except Exception as e:
        print("An error in username_password_check", e)
    return flag


def info_for_username(username):
    """
        for a given username,
        find READER_ID, FULL_NAME, DATE_OF_BIRTH, GENDER, HOMETOWN, IMAGE_URL, JOIN_DATE
    """

    ret = None
    try:
        with cx.connect('ZOIN', 'ZOIN', dsn=cx.makedsn('localhost', 1521, None, 'ORCL'),
                        encoding="UTF-8") as con:
            cur = con.cursor()
            ret = dict()
            for row in cur.execute("SELECT READER_ID, FULL_NAME, TO_CHAR(DATE_OF_BIRTH, 'YYYY, DD Month'), "
                                   "GENDER, HOMETOWN, IMAGE_URL, TO_CHAR(JOIN_DATE, 'Mon-YYYY') "
                                   "FROM PERSON INNER JOIN READER R on PERSON.PERSON_ID = R.READER_ID "
                                   "WHERE Upper(USERNAME) = Upper(:1)", [username]):
                ret['reader_id'] = row[0]
                ret['name'] = row[1]
                ret['dob'] = row[2]
                ret['gender'] = row[3]
                ret['hometown'] = row[4]
                ret['image'] = row[5]
                ret['join'] = row[6]
            ret['book'] = list()
            for row in cur.execute("SELECT BOOK_ID FROM READS WHERE READER_ID = :1", [ret['reader_id']]):
                ret['book'].append(row[0])
            ret['eval'] = list()
            for row in cur.execute("SELECT EVAL_ID FROM EVALUATION WHERE READER_ID = :1", [ret['reader_id']]):
                ret['eval'].append(row[0])
    except Exception as e:
        print("An error in info_for_username", e)
    db_log_print(ret)
    return ret


def info_for_full_name(username):
    """
        for a given full_name,
        find READER_ID, FULL_NAME, DATE_OF_BIRTH, GENDER, HOMETOWN, IMAGE_URL, JOIN_DATE
    """

    ret = None
    try:
        with cx.connect('ZOIN', 'ZOIN', dsn=cx.makedsn('localhost', 1521, None, 'ORCL'),
                        encoding="UTF-8") as con:
            cur = con.cursor()
            ret = dict()
            for row in cur.execute("SELECT READER_ID, FULL_NAME, TO_CHAR(DATE_OF_BIRTH, 'YYYY, DD Month'), "
                                   "GENDER, HOMETOWN, IMAGE_URL, TO_CHAR(JOIN_DATE, 'Mon-YYYY') "
                                   "FROM PERSON INNER JOIN READER R on PERSON.PERSON_ID = R.READER_ID "
                                   "WHERE Upper(full_name) = Upper(:1)", [username]):
                ret['reader_id'] = row[0]
                ret['name'] = row[1]
                ret['dob'] = row[2]
                ret['gender'] = row[3]
                ret['hometown'] = row[4]
                ret['image'] = row[5]
                ret['join'] = row[6]
            ret['book'] = list()
            for row in cur.execute("SELECT BOOK_ID FROM READS WHERE READER_ID = :1", [ret['reader_id']]):
                ret['book'].append(row[0])
            ret['eval'] = list()
            for row in cur.execute("SELECT EVAL_ID FROM EVALUATION WHERE READER_ID = :1", [ret['reader_id']]):
                ret['eval'].append(row[0])
    except Exception as e:
        print("An error in info_for_username", e)
    db_log_print(ret)
    return ret


def info_for_reader_id(id):
    """
        for a given username,
        find READER_ID, FULL_NAME, DATE_OF_BIRTH, GENDER, HOMETOWN, IMAGE_URL, JOIN_DATE
    """

    ret = None
    try:
        with cx.connect('ZOIN', 'ZOIN', dsn=cx.makedsn('localhost', 1521, None, 'ORCL'),
                        encoding="UTF-8") as con:
            cur = con.cursor()
            ret = dict()
            for row in cur.execute("SELECT READER_ID, FULL_NAME, TO_CHAR(DATE_OF_BIRTH, 'YYYY, DD Month'), "
                                   "GENDER, HOMETOWN, IMAGE_URL, TO_CHAR(JOIN_DATE, 'Mon-YYYY') "
                                   "FROM PERSON INNER JOIN READER R on PERSON.PERSON_ID = R.READER_ID "
                                   "WHERE READER_ID = :1", [id]):
                ret['reader_id'] = row[0]
                ret['name'] = row[1]
                ret['dob'] = row[2]
                ret['gender'] = row[3]
                ret['hometown'] = row[4]
                ret['image'] = row[5]
                ret['join'] = row[6]
            ret['book'] = list()
            for row in cur.execute("SELECT BOOK_ID FROM READS WHERE READER_ID = :1 ORDER BY BOOK_ID DESC", [ret['reader_id']]):
                ret['book'].append(row[0])
            ret['eval'] = list()
            for row in cur.execute("SELECT EVAL_ID FROM EVALUATION WHERE READER_ID = :1", [ret['reader_id']]):
                ret['eval'].append(row[0])
    except Exception as e:
        print("An error in info_for_reader_id", e)
        ret = None
    db_log_print(ret)
    return ret


def info_for_author_name(full_name):
    """
            for a given author's full name,
            find PERSON_ID, FULL_NAME, DoB, GENDER, HOMETOWN, IMAGE_URL, ABOUT, WEBPAGE
    """

    ret = None
    try:
        with cx.connect('ZOIN', 'ZOIN', dsn=cx.makedsn('localhost', 1521, None, 'ORCL'),
                        encoding="UTF-8") as con:
            cur = con.cursor()
            ret = dict()
            for row in cur.execute("SELECT PERSON_ID, FULL_NAME, TO_CHAR(DATE_OF_BIRTH, 'YYYY, DD Month'), "
                                   "GENDER, HOMETOWN, IMAGE_URL, ABOUT, WEBPAGE "
                                   "FROM PERSON P INNER JOIN AUTHOR A2 on P.PERSON_ID = A2.AUTHOR_ID "
                                   "WHERE Upper(FULL_NAME) = :1", [str(full_name).upper()]):
                ret['author_id'] = row[0]
                ret['name'] = row[1]
                ret['dob'] = row[2]
                ret['gender'] = row[3]
                ret['hometown'] = row[4]
                ret['image'] = row[5]
                ret['about'] = row[6]
                ret['webpage'] = row[7]
            ret['book'] = list()
            for row in cur.execute("SELECT BOOK_ID FROM WRITES WHERE AUTHOR_ID = :1 ORDER BY BOOK_ID DESC", [ret['author_id']]):
                ret['book'].append(row[0])
    except Exception as e:
        print("An error in info_for_author_name", e)
        db_log_print(e)
        ret = None
    db_log_print(ret)
    return ret


def info_for_author_id(id):
    """
            for a given author's brs id,
            find PERSON_ID, FULL_NAME, DoB, GENDER, HOMETOWN, IMAGE_URL, ABOUT, WEBPAGE
    """

    ret = None
    try:
        with cx.connect('ZOIN', 'ZOIN', dsn=cx.makedsn('localhost', 1521, None, 'ORCL'),
                        encoding="UTF-8") as con:
            cur = con.cursor()
            ret = dict()

            for row in cur.execute("SELECT PERSON_ID, FULL_NAME, TO_CHAR(DATE_OF_BIRTH, 'YYYY, DD Month'), "
                                   "GENDER, HOMETOWN, IMAGE_URL, ABOUT, WEBPAGE "
                                   "FROM PERSON P INNER JOIN AUTHOR A2 on P.PERSON_ID = A2.AUTHOR_ID "
                                   "WHERE PERSON_ID = :1", [id]):

                ret['author_id'] = row[0]
                ret['name'] = row[1]
                ret['dob'] = row[2]
                ret['gender'] = row[3]
                ret['hometown'] = row[4]
                ret['image'] = row[5]
                ret['about'] = row[6]
                ret['webpage'] = row[7]
            ret['book'] = list()
            for row in cur.execute("SELECT BOOK_ID FROM WRITES WHERE AUTHOR_ID = :1 ORDER BY BOOK_ID DESC", [ret['author_id']]):
                ret['book'].append(row[0])
    except Exception as e:
        print("An error in info_for_author_id", e)
        db_log_print(e)
        ret = None
    db_log_print(ret)
    return ret


def info_for_book_title(title):
    """
    :param title:title_of_a_book
    :return: BOOK_ID, PUBLISHER_NAME, TITLE, PUBLICATION_DATE, ISBN, LANGUAGE, NUM_PAGES, IMAGE_URL, DESCRIPTION "
    """
    ret = None
    try:
        with cx.connect('ZOIN', 'ZOIN', dsn=cx.makedsn('localhost', 1521, None, 'ORCL'),
                        encoding="UTF-8") as con:
            cur = con.cursor()
            ret = dict()
            for row in cur.execute("SELECT BOOK_ID, PUBLISHER_NAME, TITLE, "
                                   "TO_CHAR(PUBLICATION_DATE, 'YYYY, DD Month'), "
                                   "ISBN, LANGUAGE, NUM_PAGES, IMAGE_URL, DESCRIPTION "
                                   "FROM BOOK LEFT JOIN PUBLISHER P on P.PUBLISHER_ID = BOOK.PUBLISHER_ID "
                                   "WHERE Upper(TITLE) = :1", [str(title).upper()]):
                ret['book_id'] = row[0]
                ret['pub_name'] = row[1]
                ret['title'] = row[2]
                ret['pub_date'] = row[3]
                ret['isbn'] = row[4]
                ret['language'] = row[5]
                ret['num_pages'] = row[6]
                ret['image'] = row[7]
                ret['description'] = row[8]
            ret['genre'] = list()
            for row in cur.execute("SELECT GENRE_NAME FROM GENRE, OF_GENRE WHERE OF_GENRE.GENRE_ID = GENRE.GENRE_ID "
                                   "AND OF_GENRE.BOOK_ID = :1", [ret['book_id']]):
                ret['genre'].append(row[0])
            ret['author'] = list()
            for row in cur.execute("SELECT WRITES.AUTHOR_ID FROM WRITES WHERE BOOK_ID = :1", [ret['book_id']]):
                ret['author'].append(row[0])
            ret['eval'] = list()
            for row in cur.execute("SELECT EVAL_ID FROM EVALUATION WHERE BOOK_ID = :1", [ret['book_id']]):
                ret['eval'].append(row[0])
    except Exception as e:
        print("An error in info_for_book_title", title, e)
        db_log_print(e)
        ret = None
    db_log_print(ret)
    return ret


def info_for_book_id(id):
    """
    :param id: goodreads_id_of_a_book
    :return: BOOK_ID, PUBLISHER_NAME, TITLE, PUBLICATION_DATE, ISBN, LANGUAGE, NUM_PAGES, IMAGE_URL, DESCRIPTION "
    """
    ret = None
    try:
        with cx.connect('ZOIN', 'ZOIN', dsn=cx.makedsn('localhost', 1521, None, 'ORCL'),
                        encoding="UTF-8") as con:
            cur = con.cursor()
            ret = dict()
            for row in cur.execute("SELECT BOOK_ID, PUBLISHER_NAME, TITLE, "
                                   "TO_CHAR(PUBLICATION_DATE, 'YYYY, DD Month'), "
                                   "ISBN, LANGUAGE, NUM_PAGES, IMAGE_URL, DESCRIPTION "
                                   "FROM BOOK LeFT JOIN PUBLISHER P on P.PUBLISHER_ID = BOOK.PUBLISHER_ID "
                                   "WHERE BOOK_ID = :1", [id]):
                ret['book_id'] = row[0]
                ret['pub_name'] = row[1]
                ret['title'] = row[2]
                ret['pub_date'] = row[3]
                ret['isbn'] = row[4]
                ret['language'] = row[5]
                ret['num_pages'] = row[6]
                ret['image'] = row[7]
                ret['description'] = row[8]
            ret['genre'] = list()
            for row in cur.execute("SELECT GENRE_NAME FROM GENRE, OF_GENRE WHERE OF_GENRE.GENRE_ID = GENRE.GENRE_ID "
                                   "AND OF_GENRE.BOOK_ID = :1", [ret['book_id']]):
                ret['genre'].append(row[0])
            ret['author'] = list()
            for row in cur.execute("SELECT WRITES.AUTHOR_ID FROM WRITES WHERE BOOK_ID = :1", [ret['book_id']]):
                ret['author'].append(row[0])
            ret['eval'] = list()
            for row in cur.execute("SELECT EVAL_ID FROM EVALUATION WHERE BOOK_ID = :1", [ret['book_id']]):
                ret['eval'].append(row[0])
    except Exception as e:
        print(ret)
        print("An error in info_for_book_id", id, e)
        db_log_print(e)
        ret = None
    db_log_print(ret)
    return ret


def books_of_a_genre(genre_name):
    """
    :param genre_name:
    :return: all book ids of that genre
    """
    try:
        with cx.connect('ZOIN', 'ZOIN', dsn=cx.makedsn('localhost', 1521, None, 'ORCL'),
                        encoding="UTF-8") as con:
            cur = con.cursor()
            ret = dict()
            ret['book'] = list()
            for row in cur.execute("SELECT BOOK_ID FROM GENRE, OF_GENRE "
                                   "WHERE Upper(GENRE_NAME) = :1"
                                   "AND GENRE.GENRE_ID = OF_GENRE.GENRE_ID ", [genre_name.upper()]):
                ret['book'].append(row[0])
    except Exception as e:
        print("An error in books_of_a_genre", e)
        db_log_print(e)
        ret = None
    db_log_print(ret)
    return ret


def books_of_a_publisher(publisher_name):
    """
    :param publisher_name:
    :return: all book ids of that genre
    """
    try:
        with cx.connect('ZOIN', 'ZOIN', dsn=cx.makedsn('localhost', 1521, None, 'ORCL'),
                        encoding="UTF-8") as con:
            cur = con.cursor()
            ret = dict()
            ret['book'] = list()
            for row in cur.execute("SELECT BOOK_ID FROM BOOK INNER JOIN PUBLISHER P on P.PUBLISHER_ID = BOOK.PUBLISHER_ID "
                                   "WHERE upper(PUBLISHER_NAME) = :1", [publisher_name.upper()]):
                ret['book'].append(row[0])
    except Exception as e:
        print("An error in books_of_a_publisher", e)
        db_log_print(e)
        ret = None
    db_log_print(ret)
    return ret


def books_of_a_language(language_name):
    """
    :param language_name:
    :return: all book ids of that genre
    """
    try:
        with cx.connect('ZOIN', 'ZOIN', dsn=cx.makedsn('localhost', 1521, None, 'ORCL'),
                        encoding="UTF-8") as con:
            cur = con.cursor()
            ret = dict()
            ret['book'] = list()
            for row in cur.execute("SELECT BOOK_ID FROM BOOK WHERE upper(LANGUAGE) = :1", [language_name.upper()]):
                ret['book'].append(row[0])
    except Exception as e:
        print("An error in books_of_a_language", e)
        db_log_print(e)
        ret = None
    db_log_print(ret)
    return ret


def info_for_eval_id(eval_id):
    try:
        with cx.connect('ZOIN', 'ZOIN', dsn=cx.makedsn('localhost', 1521, None, 'ORCL'),
                        encoding="UTF-8") as con:
            cur = con.cursor()
            ret = dict()
            for row in cur.execute("SELECT RATING, REVIEW, DATE_UPDATED, B.BOOK_ID, TITLE, IMAGE_URL "
                                "FROM EVALUATION INNER JOIN BOOK B on B.BOOK_ID = EVALUATION.BOOK_ID "
                                   "WHERE EVAL_ID  = :1", [eval_id]):
                ret['rating'] = row[0]
                ret['review'] = row[1]
                ret['date'] = row[2]
                ret['book_id'] = row[3]
                ret['title'] = row[4]
                ret['image'] = row[5]
    except Exception as e:
        print("An error in info_for_eval_id", e)
        db_log_print(e)
        ret = None
    db_log_print(ret)
    return ret


def info_reader_for_eval_id(eval_id):
    try:
        with cx.connect('ZOIN', 'ZOIN', dsn=cx.makedsn('localhost', 1521, None, 'ORCL'),
                        encoding="UTF-8") as con:
            cur = con.cursor()
            ret = dict()
            for row in cur.execute("SELECT RATING, REVIEW, to_char(DATE_UPDATED, 'YYYY, DD MONTH'), BOOK_ID,"
                                   " READER_ID, PERSON_ID, FULL_NAME, IMAGE_URL "
                                   " FROM EVALUATION INNER JOIN PERSON ON READER_ID = PERSON_ID "
                                   " WHERE EVAL_ID =  :1", [eval_id]):
                ret['rating'] = row[0]
                ret['review'] = row[1]
                ret['date'] = row[2]
                ret['book_id'] = row[3]
                ret['reader_id'] = row[5]
                ret['full_name'] = row[6]
                ret['image'] = row[7]
    except Exception as e:
        print("An error in info_for_eval_id", e)
        db_log_print(e)
        ret = None
    db_log_print(ret)
    return ret


class MyRecommender:
    def __init__(self):
        try:
            with cx.connect('ZOIN', 'ZOIN', dsn=cx.makedsn('localhost', 1521, None, 'ORCL'),
                            encoding="UTF-8") as con:
                cur = con.cursor()
                frame = pd.read_sql('''SELECT BOOK_ID, READER_ID, MAX(RATING) as M 
                                        FROM EVALUATION
                                        GROUP BY BOOK_ID, READER_ID''', con=con)
                self.frame = frame.rename(columns={
                    'BOOK_ID': 'item_id', 'READER_ID': 'user_id', 'M': 'rating'
                })
                (
                    self.X_train_initial,
                    self.y_train_initial,
                    self.X_train_update,
                    self.y_train_update,
                    self.X_test_update,
                    self.y_test_update,
                ) = train_update_test_split(self.frame, 0.01)
                self.matrix_fact = KernelMF(n_epochs=20, n_factors=100, verbose=1, lr=0.001, reg=0.005)
                self.matrix_fact.fit(self.X_train_initial, self.y_train_initial)
                print('Fitting done.')
        except Exception as e:
            print("An error in constructing the recommender")
            pass

    def list_recommended_books(self, reader_id):
        items_known = self.X_train_initial.query("user_id == @reader_id")["item_id"]
        ret = self.matrix_fact.recommend(user=reader_id, items_known=items_known, amount=10)
        return ret['item_id']

if __name__ == '__main__':
    print("ewfr")