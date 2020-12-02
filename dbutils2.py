import cx_Oracle as cx
import time
from flask_bcrypt import check_password_hash, generate_password_hash
import dbutils

""""
with cx.connect('ZOIN', 'ZOIN', dsn=cx.makedsn('localhost', 1521, None, 'ORCL'),
                        encoding="UTF-8") as con:            
                        """
# D:/app/USER/product/11.2.0/dbhome_1/instantclient


def db_log_print(text, **kwargs):
    with open('db_log_2.txt', 'a', encoding='UTF-8') as file:
        print("\n", file=file)
        print(time.asctime(), file=file)
        print(text, kwargs, file=file)


def register_into_db(fullname, username, email, password, hometown, dob, image, gender, join_date = time.strftime('%Y-%m-%d')):
    try:
        if str(username).lower() == 'admin':
            return False
        with cx.connect('ZOIN', 'ZOIN', dsn=cx.makedsn('localhost', 1521, None, 'ORCL'),
                        encoding="UTF-8") as con:
            cur = con.cursor()
            print("Join date, ", join_date)
            if gender.lower()[0] == 'm':
                gender = 'M'
            elif gender.lower()[0] == 'f':
                gender = 'F'
            else:
                gender = ''
            cur.execute("INSERT INTO PERSON (FULL_NAME, DATE_OF_BIRTH, HOMETOWN, IMAGE_URL, GENDER) "
                        "VALUES (:1, to_date(:2, 'YYYY-DD-MM'), :3, :4, :5)",
                        [fullname, dob, hometown, image, gender])
            # print('Halfway')
            _id = ''
            for x in cur.execute("SELECT PERSON_SEQUENCE.currval FROM DUAL"):
                _id = x[0]

            cur.execute("INSERT INTO READER(READER_ID, USERNAME, PASSWORD_HASH, EMAIL, JOIN_DATE) "
                        "VALUES (:1, :2, :3, :4, to_date(:5, 'YYYY-MM-DD'))",
                        [_id, username, generate_password_hash(password), email, join_date])
            print("Insertion should be done!")

            con.commit()
            return True
    except Exception as e:
        print('Exception in register:', e)
    return False


def check_username_password(username, password):

    flag = None
    try:
        with cx.connect('ZOIN', 'ZOIN', dsn=cx.makedsn('localhost', 1521, None, 'ORCL'),
                        encoding="UTF-8") as con:
            cur = con.cursor()
            p_hash = ""
            for r in cur.execute("SELECT PASSWORD_HASH, READER_ID FROM READER WHERE USERNAME = :1",
                                 [username]):
                p_hash = r[0]
                if check_password_hash(p_hash, password):
                    flag = r[1]
                    break
    except Exception as e:
            print('Exception in dbutils2 check_username_password', e)
    return flag


def update_password_to_entropy():
    try:
        with cx.connect('ZOIN', 'ZOIN', dsn=cx.makedsn('localhost', 1521, None, 'ORCL'),
                        encoding="UTF-8") as con:
            cur = con.cursor()
            r_ids = []
            for r in cur.execute('SELECT READER_ID FROM READER'):
                r_ids += [r]
            for r in r_ids:
                cur.execute('UPDATE READER SET PASSWORD_HASH = :1 WHERE READER_ID = :2', [generate_password_hash('entropy').decode('UTF-8'), r[0]])
            con.commit()
    except Exception as e:
        return 'Hello '+ str(e)


def wish_or_read(reader_id, book_id, flag = 'r'):
    try:
        with cx.connect('ZOIN', 'ZOIN', dsn=cx.makedsn('localhost', 1521, None, 'ORCL'),
                        encoding="UTF-8") as con:
            cur = con.cursor()
            table = 'READS'
            if flag == 'w':
                table = 'WISHES'
            cur.execute("INSERT INTO " + table + " VALUES (:1, :2)", [reader_id, book_id])
            print(flag + " insertion should be done!")
            con.commit()
            return True
    except Exception as e:
        print('Exception in wish or read:', e)
    return False


def check_wish_read_or_eval(reader_id, book_id, mode ='r'):
    flag = False
    try:
        with cx.connect('ZOIN', 'ZOIN', dsn=cx.makedsn('localhost', 1521, None, 'ORCL'),
                        encoding="UTF-8") as con:
            cur = con.cursor()
            table = 'READS'
            if mode == 'w':
                table = 'WISHES'
            elif mode == 'e':
                table = "EVALUATION"
            for i in cur.execute("SELECT * FROM " + table + " WHERE READER_ID = :1 "
                                        "AND BOOK_ID = :2", [reader_id, book_id]):
                flag = True
            print(str(flag) + ", check should be done!")
            con.commit()
    except Exception as e:
        print('Exception in check_wish_read_or_eval:', e)
    return flag


def insert_evaluation(reader_id, book_id, rating, review=''):
    cur_time = time.strftime('%d-%b-%Y')
    print(cur_time)
    try:
        with cx.connect('ZOIN', 'ZOIN', dsn=cx.makedsn('localhost', 1521, None, 'ORCL'),
                        encoding="UTF-8") as con:
            cur = con.cursor()
            cur.execute("INSERT INTO EVALUATION (RATING, REVIEW, BOOK_ID, READER_ID,"
                        " DATE_ADDED, DATE_UPDATED)  VALUES (:1, :2, :3, :4, :5, :5)"
                        , [rating, review, book_id, reader_id, cur_time, cur_time])
            con.commit()
            return True
    except Exception as e:
        print('Exception in insert_eval: ', e)
    return False


def find_all_genres():
    print('it came to all_genres')
    try:
        with cx.connect('ZOIN', 'ZOIN', dsn=cx.makedsn('localhost', 1521, None, 'ORCL'),
                        encoding="UTF-8") as con:
            cur = con.cursor()
            ret = []
            for row in cur.execute("SELECT GENRE_NAME, COUNT(DISTINCT BOOK_ID) AS CNT"
                            " FROM GENRE INNER JOIN OF_GENRE OG on GENRE.GENRE_ID = OG.GENRE_ID"
                            " GROUP BY GENRE_NAME ORDER BY CNT DESC"):
                # print(row)
                ret += [row]
            print(len(ret))
    except Exception as e:
        ret = None
        print('Exception in all_genres: ', e)
    return ret


def find_all_authors():
    print('it came to all_authors')
    try:
        with cx.connect('ZOIN', 'ZOIN', dsn=cx.makedsn('localhost', 1521, None, 'ORCL'),
                        encoding="UTF-8") as con:
            cur = con.cursor()
            ret = []
            for row in cur.execute("SELECT FULL_NAME, COUNT(DISTINCT BOOK_ID) AS CNT "
                                   " FROM PERSON INNER JOIN WRITES "" ON AUTHOR_ID = PERSON_ID"
                                   " GROUP BY FULL_NAME ORDER BY CNT DESC, full_name desc"):
                # print(row)
                ret += [row]
            print(len(ret))
    except Exception as e:
        ret = None
        print('Exception in all_authors: ', e)
    return ret


def find_all_languages():
    print('it came to all_languages')
    try:
        with cx.connect('ZOIN', 'ZOIN', dsn=cx.makedsn('localhost', 1521, None, 'ORCL'),
                        encoding="UTF-8") as con:
            cur = con.cursor()
            ret = []
            for row in cur.execute("SELECT LANGUAGE, COUNT(DISTINCT BOOK_ID) AS CNT "
                                   "FROM BOOK WHERE LANGUAGE IS NOT NULL  "
                                   "GROUP BY LANGUAGE ORDER BY CNT desc"):
                ret += [row]
            print(len(ret))
    except Exception as e:
        ret = None
        print('Exception in all_languages: ', e)
    return ret


def find_all_publishers():
    print('it came to all_publishers')
    try:
        with cx.connect('ZOIN', 'ZOIN', dsn=cx.makedsn('localhost', 1521, None, 'ORCL'),
                        encoding="UTF-8") as con:
            cur = con.cursor()
            ret = []
            for row in cur.execute("SELECT PUBLISHER_NAME, COUNT(DISTINCT BOOK_ID) AS CNT "
                                   "FROM BOOK INNER JOIN PUBLISHER P on P.PUBLISHER_ID = BOOK.PUBLISHER_ID "
                                   "GROUP BY PUBLISHER_NAME ORDER BY CNT DESC"):
                ret += [row]
            print(len(ret))
    except Exception as e:
        ret = None
        print('Exception in all_publishers: ', e)
    return ret


def admin_add_author_db(FULL_NAME_, DATE_OF_BIRTH_, HOMETOWN_, IMAGE_URL_, gender, ABOUT_, WEBPAGE_):
    try:
        with cx.connect('ZOIN', 'ZOIN', dsn=cx.makedsn('localhost', 1521, None, 'ORCL'),
                        encoding="UTF-8") as con:
            cur = con.cursor()
            if gender.lower()[0] == 'm':
                gender = 'M'
            elif gender.lower()[0] == 'f':
                gender = 'F'
            else:
                gender = ''
            cur.callproc('AUTHOR_INSERT', [FULL_NAME_, DATE_OF_BIRTH_, HOMETOWN_, IMAGE_URL_, gender, ABOUT_, WEBPAGE_])
            con.commit()
            return True
    except Exception as e:
        print('Exception in admin_add_author_db: ', e)
        return False


def admin_add_author_db(FULL_NAME_, DATE_OF_BIRTH_, HOMETOWN_, IMAGE_URL_, gender, ABOUT_, WEBPAGE_):
    try:
        with cx.connect('ZOIN', 'ZOIN', dsn=cx.makedsn('localhost', 1521, None, 'ORCL'),
                        encoding="UTF-8") as con:
            cur = con.cursor()
            if gender.lower()[0] == 'm':
                gender = 'M'
            elif gender.lower()[0] == 'f':
                gender = 'F'
            else:
                gender = ''
            cur.callproc('AUTHOR_INSERT', [FULL_NAME_, DATE_OF_BIRTH_, HOMETOWN_, IMAGE_URL_, gender, ABOUT_, WEBPAGE_])
            con.commit()
            return True
    except Exception as e:
        print('Exception in admin_add_author_db: ', e)
        return False


def admin_add_book_db(authors, genres, TITLE, PUBLICATION_DATE, ISBN, LANGUAGE, NUM_PAGES, IMAGE_URL, DESCRIPTION, PUBLISHER_NAME, COUNTRY):
    try:
        with cx.connect('ZOIN', 'ZOIN', dsn=cx.makedsn('localhost', 1521, None, 'ORCL'),
                        encoding="UTF-8") as con:
            cur = con.cursor()
            authors = [str(i).strip() for i in authors.split(',')]
            author_ids = []
            for author in authors:
                ret = dbutils.info_for_author_name(author)
                if ret is None:
                    print("Author not found")
                    return -1
                author_ids += [ret.get('author_id')]
            genres = [str(i).strip() for i in genres.split(',')]
            genre_ids = []
            for genre in genres:
                ret_val = cur.callfunc('genre_number_or_insert', int, [genre])
                genre_ids += [ret_val]
            cur.callproc('book_insert', [TITLE, PUBLICATION_DATE, ISBN, LANGUAGE
                , NUM_PAGES, IMAGE_URL, DESCRIPTION, PUBLISHER_NAME, COUNTRY])
            con.commit()
            return True
    except Exception as e:
        print('Exception in admin_add_book_db: ', e)
        return False
