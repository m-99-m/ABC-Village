""" DBのtable設計とCRUDメソッド群 """
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, current_user
from flask_bcrypt import generate_password_hash, check_password_hash
from datetime import datetime
from AtCoder import get_username
from app import app
import os
#DB_URI = 'sqlite:///test.sqlite'
DB_URI = 'postgresql://apaqwsskbylfcn:4bc4926ac0568ce60f5d9f6aae0fcbc636976d23f4a62d2e105d9985beb4503a@ec2-54-156-24-159.compute-1.amazonaws.com:5432/dp8kqnh14jgmv'
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["SECRET_KEY"] = "Gubuugubuusaffsaffmogeinad033"

db = SQLAlchemy(app)
login_manager = LoginManager(app)

def get_needVP():
    ret = [[0, 0], [600, 0]]
    for i in range(97):
        ret.append([ret[i+1][0] + (ret[i+1][0]*19)//855, 0])
    for i in range(46):
        ret[98-i][0] += 1
    for i in range(98):
        ret[i+1][1] = ret[i][1] + ret[i+1][0]
    return ret

def get_next_needVP(level):
    if level<=0 or level>=99:
        return 0
    ret = get_needVP()
    return ret[level][0]


def is_admin():
    if current_user.is_authenticated and current_user.username == 'm_99':
        return True
    return False

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


class User(db.Model, UserMixin):
    """ ログインセッションを管理するUserテーブル """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), index=True)
    inner_username = db.Column(db.String(32), index=True)
    password = db.Column(db.Text)
    VP = db.Column(db.Integer)
    level = db.Column(db.Integer)
    register_time = db.Column(db.DateTime, default=datetime.now())

    def __init__(self, username, password):
        """ ユーザ名、パスワードが入力必須 """
        self.username = get_username(username)
        self.inner_username = username.lower()
        self.password = generate_password_hash(password).decode('utf-8')
        self.VP = 0
        self.level = 1
        self.register_time = datetime.now()
        self.register_time = self.register_time\
            .replace(microsecond=0)

    def check_password(self, password):
        """ パスワードをチェックしてTrue/Falseを返す """
        return check_password_hash(self.password, password)

    def reset_password(self, password):
        """ 再設定されたパスワードをDBにアップデート """
        self.password = generate_password_hash(password).decode('utf-8')

    @classmethod
    def select_by_username(cls, username):
        return cls.query.filter_by(inner_username=username.lower()).first()

    @classmethod
    def get_ranking_info(cls):
        return cls.query.with_entities(cls.username, cls.level, cls.VP).all()

class Contest(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    starttime = db.Column(db.DateTime)
    index = db.Column(db.Integer)

    def __init__(self, index, starttime):
        self.index = index
        self.starttime = starttime

    @classmethod
    def get_contests_info(cls):
        return cls.query.all()

    @classmethod
    def select_by_index(cls, index):
        return cls.query.filter_by(index=index).first()

