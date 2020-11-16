from flask_login import *


class Reader(UserMixin):

    def __init__(self, rid, username, pw):
        self.rid = rid
        self.username = username
        self.pw = pw


