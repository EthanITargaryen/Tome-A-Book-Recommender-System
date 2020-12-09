import cx_Oracle as cx
import time
from flask_bcrypt import check_password_hash, generate_password_hash
import dbutils
import pandas as pd

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


def update_password(username, old_password, new_password):
    if check_username_password(username, old_password):
        try:
            with cx.connect('ZOIN', 'ZOIN', dsn=cx.makedsn('localhost', 1521, None, 'ORCL'),
                            encoding="UTF-8") as con:
                cur = con.cursor()
                cur.execute('UPDATE READER SET PASSWORD_HASH = :1 '
                            'WHERE USERNAME = :2', [generate_password_hash(new_password), username])
                con.commit()
                return True
        except Exception as e:
            print('Exception in dbutils2 update_password', e)
    return False



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


def follow_an_author(author_id, reader_id):
    try:
        with cx.connect('ZOIN', 'ZOIN', dsn=cx.makedsn('localhost', 1521, None, 'ORCL'),
                        encoding="UTF-8") as con:
            cur = con.cursor()
            cur.execute('INSERT INTO FOLLOWS (FOLLOWER, FOLLOWED) VALUES (:1, :2)', [reader_id, author_id])
            print(author_id + " following should be done!")
            con.commit()
            return True
    except Exception as e:
        print('Exception in follow:', e)
    return False


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


def check_follow(reader_id, author_id):
    flag = False
    try:
        with cx.connect('ZOIN', 'ZOIN', dsn=cx.makedsn('localhost', 1521, None, 'ORCL'),
                        encoding="UTF-8") as con:
            cur = con.cursor()
            for i in cur.execute("SELECT * FROM FOLLOWS WHERE FOLLOWER = :1 AND FOLLOWED = :2"
                    , [reader_id, author_id]):
                flag = True
            print(str(flag) + ", follow-check should be done!")
            con.commit()
    except Exception as e:
        print('Exception in check_follow:', e)
    return flag


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


def substr_search(x):
    x = '%%' + str(x).lower() + '%%'
    ret = dict()
    try:
        with cx.connect('ZOIN', 'ZOIN', dsn=cx.makedsn('localhost', 1521, None, 'ORCL'),
                        encoding="UTF-8") as con:
            cur = con.cursor()
            ret['books'] = list()
            ret['authors'] = list()
            ret['readers'] = list()
            ret['publishers'] = list()
            for r in cur.execute("""
                SELECT BOOK_ID, TITLE FROM BOOK WHERE LOWER(TITLE) LIKE :1 
                    ORDER BY TITLE 
                            """, [x]):
                ret['books'] += [r]
            for r in cur.execute("""
                SELECT AUTHOR_ID, FULL_NAME FROM AUTHOR INNER JOIN PERSON P on P.PERSON_ID = AUTHOR.AUTHOR_ID
                    WHERE lower(FULL_NAME) LIKE :1 
                    ORDER BY FULL_NAME 
                            """, [x]):
                ret['authors'] += [r]
            for r in cur.execute("""
                SELECT READER_ID, FULL_NAME FROM READER INNER JOIN PERSON P on P.PERSON_ID = READER.READER_ID
                    WHERE lower(FULL_NAME) LIKE :1
                    ORDER BY FULL_NAME 
                            """, [x]):
                ret['readers'] += [r]
            for r in cur.execute("""
                SELECT PUBLISHER_ID, PUBLISHER_NAME FROM PUBLISHER WHERE lower(PUBLISHER_NAME) LIKE :1
                     ORDER BY PUBLISHER_NAME     """, [x]):
                ret['publishers'] += [r]
            keys = ret.keys()
            for x in keys:
                if len(ret[x]) == 0:
                    ret[x] = False
    except Exception as e:
        print('An exception in substring search:', x, ' ', e)
    return ret


def comments_for_book_id(b_id):
    ret = dict()
    try:
        with cx.connect('ZOIN', 'ZOIN', dsn=cx.makedsn('localhost', 1521, None, 'ORCL'),
                        encoding="UTF-8") as con:
            cur = con.cursor()
            ret['comments'] = list()
            cur.execute("""SELECT COMMENT_TEXT, USERNAME, IMAGE_URL
                            , COMMENT_ID, TO_CHAR(TIME, 'HH24:MI DD-MM-YYYY') T
                            FROM COMMENT_THREAD INNER JOIN PERSON ON PERSON_ID = READER_ID
                                INNER JOIN READER R2 on PERSON.PERSON_ID = R2.READER_ID
                            WHERE BOOK_ID = :1 AND PARENT_COMMENT IS NULL ORDER BY TIME DESC""", [b_id])
            records = cur.fetchall()
            for r in records:
                replies = list()
                for j in cur.execute("""SELECT COMMENT_TEXT, USERNAME, IMAGE_URL
                                        , TO_CHAR(TIME, 'HH24:MI DD-MM-YYYY') T
                                        FROM COMMENT_THREAD INNER JOIN PERSON ON PERSON_ID = READER_ID
                                            INNER JOIN READER R2 on PERSON.PERSON_ID = R2.READER_ID
                                        WHERE PARENT_COMMENT = :1 ORDER BY TIME""", [r[3]]):
                    replies.append((j[0], j[1], j[2], j[3]))
                replies = tuple(replies)
                ret['comments'] += [(r[0], replies, r[1], r[2], r[4], str(r[3]))]
                # print(ret['comments'][-1])
            for r in cur.execute('SELECT TITLE, IMAGE_URL FROM BOOK WHERE BOOK_ID = :1', [b_id]):
                ret['title'] = r[0]
                ret['image'] = r[1]
                print(ret['title'])
            ret['replies'] = list()

    except Exception as e:
        print('An exception in comment for book id ', b_id, ': ', e)
        ret = None
    return ret


def insert_comment(text, b_id, r_id, par_id = '', ctime = time.strftime('%Y-%m-%d %H:%M:%S')):
    try:
        with cx.connect('ZOIN', 'ZOIN', dsn=cx.makedsn('localhost', 1521, None, 'ORCL'),
                        encoding="UTF-8") as con:
            cur = con.cursor()
            cur.execute('''INSERT INTO COMMENT_THREAD (COMMENT_TEXT, PARENT_COMMENT, BOOK_ID, READER_ID, TIME) VALUES 
                            (:1, :2, :3, :4, to_timestamp(:5, 'YYYY-MM-DD HH24:MI:SS'))''', [text, par_id, b_id, r_id, ctime])
            con.commit()
            return True
    except Exception as e:
        print('An exception in commenting', b_id, ': ', e)
    return False


def authors_following(r_id):
    ret = dict()
    try:
        with cx.connect('ZOIN', 'ZOIN', dsn=cx.makedsn('localhost', 1521, None, 'ORCL'),
                        encoding="UTF-8") as con:
            cur = con.cursor()
            ret['fols'] = list()
            for r in cur.execute("SELECT FOLLOWED FROM FOLLOWS WHERE FOLLOWER = :1", [r_id]):
                ret['fols'].append(r[0])
            print(ret['fols'])
            return ret
    except Exception as e:
        print('An exception in retrieving the followed', r_id, ': ', e)
    return None
