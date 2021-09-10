from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, current_user
from flask_bcrypt import generate_password_hash, check_password_hash
from datetime import datetime
from AtCoder import get_username
from app import app
import os
#DB_URI = 'sqlite:///test.sqlite'

DB_URI = 'postgresql://lwyhxoijhformz:bb2f1919248cd6cee1e6a82295ff3b6f8fa450b0150760bcfeec35785f261fb9@ec2-44-195-16-34.compute-1.amazonaws.com:5432/dduln92gpjjt49'
#'postgresql-clear-91092'#postgresql://apaqwsskbylfcn:4bc4926ac0568ce60f5d9f6aae0fcbc636976d23f4a62d2e105d9985beb4503a@ec2-54-156-24-159.compute-1.amazonaws.com:5432/dp8kqnh14jgmv'
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
    if level <= 0 or level >= 99:
        return 0
    ret = get_needVP()
    return ret[level][0]


def is_admin():
    if current_user.is_authenticated and current_user.username == 'm_99':
        return True
    return False


def is_contest_running():
    contests = Contest.get_contests_info()
    d = datetime.now()
    for c in contests:
        if (c.starttime - d).total_seconds() <= 0:
            return 1

    return 0


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), index=True)
    inner_username = db.Column(db.String(32), index=True)
    password = db.Column(db.Text)
    VP = db.Column(db.Integer)
    level = db.Column(db.Integer)
    register_time = db.Column(db.DateTime, default=datetime.now())

    champion_medal = db.Column(db.Integer, default=0)
    complete_medal = db.Column(db.Integer, default=0)
    special_medal = db.Column(db.Integer, default=0)

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
        return check_password_hash(self.password, password)

    def reset_password(self, password):
        self.password = generate_password_hash(password).decode('utf-8')

    @classmethod
    def select_by_id(cls, id):
        return cls.query.filter_by(id=id).first()

    @classmethod
    def select_by_username(cls, username):
        return cls.query.filter_by(inner_username=username.lower()).first()

    @classmethod
    def select_by_register_time(cls, time):
        return cls.query.filter((time-cls.register_time).total_seconds > 0)

    @classmethod
    def select_all(cls):
        return cls.query.order_by(cls.id).all()


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


class History(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    recode_time = db.Column(db.DateTime)
    user_id = db.Column(db.Integer)
    incremental = db.Column(db.Integer)
    message = db.Column(db.String(255), index=True)

    def __init__(self, user_id, incremental):
        self.recode_time = datetime.now()
        self.recode_time = self.recode_time \
            .replace(microsecond=0)
        self.user_id = user_id
        self.incremental = incremental
        self.message = ''

    @classmethod
    def select_by_user_id(cls, user_id):
        return cls.query.filter_by(user_id=user_id).order_by(cls.recode_time).all()


class HisLevelUp(History):
    level_from = db.Column(db.Integer)

    def __init__(self, user_id, incremental, level_from):
        super().__init__(user_id, incremental)
        self.level_from = level_from
        self.message = 'LvUP: ' + str(level_from) + ' -> ' + str(level_from+1)


class HisContestWin(History):
    rank = db.Column(db.Integer)
    score = db.Column(db.Integer)
    contest_index = db.Column(db.Integer)

    def __init__(self, user_id, incremental, contest_index, rank, score):
        super().__init__(user_id, incremental)
        self.contest_index = contest_index
        self.rank = rank
        self.score = score
        self.message = 'ABC' + str(contest_index) + 'で' + str(score) + '点 (' + str(rank) + '位)となった報酬の付与'


class HisBattleResult(History):
    bet = db.Column(db.Integer)
    other_id = db.Column(db.Integer)
    contest_index2 = db.Column(db.Integer)
    is_mine = db.Column(db.Integer)
    battle_result = db.Column(db.Integer)
    bet = db.Column(db.Integer)

    def __init__(self, user_id, incremental, contest_index2, other_id, is_mine, battle_result, bet):
        super().__init__(user_id, incremental)
        self.contest_index2 = contest_index2
        self.other_id = other_id
        self.is_mine = is_mine
        self.battle_result = battle_result
        self.bet = bet
        self.message = 'ABC' + str(contest_index2) + 'で' + User.select_by_id(other_id).username + 'に'
        if is_mine:
            self.message += '申請したベットVP: '
        else:
            self.message += '申請されたベットVP: '
        self.message += str(bet)
        self.message += 'の対決に'
        if battle_result == 1:
            self.message += '勝つ'
        elif battle_result == 0:
            self.message += '引き分ける'
        else:
            self.message += '負ける'


class HisBet(History):
    to_id = db.Column(db.Integer)

    def __init__(self, user_id, incremental, to_id):
        super().__init__(user_id, incremental)
        self.to_id = to_id
        user = User.select_by_id(to_id)
        self.message = str(user.username) + 'に対戦を申請する'


class HisBet2(HisBet):

    def __init__(self, user_id, incremental, to_id):
        super().__init__(user_id, incremental, to_id)
        user = User.select_by_id(to_id)
        self.message = str(user.username) + 'から申請された対戦を受ける'


class HisCancel(HisBet):

    def __init__(self, user_id, incremental, to_id):
        super().__init__(user_id, incremental, to_id)
        user = User.select_by_id(to_id)
        self.message = str(user.username) + 'に申請した対戦をキャンセル'


class HisDenied(HisBet):

    def __init__(self, user_id, incremental, to_id):
        super().__init__(user_id, incremental, to_id)
        user = User.select_by_id(to_id)
        self.message = str(user.username) + 'に申請した対戦を断られる'


class HisStop0(HisBet):

    def __init__(self, user_id, incremental, to_id):
        super().__init__(user_id, incremental, to_id)
        user = User.select_by_id(to_id)
        self.message = str(user.username) + 'に申請した対戦が中止になる'


class HisStop1(HisBet):

    def __init__(self, user_id, incremental, to_id):
        super().__init__(user_id, incremental, to_id)
        user = User.select_by_id(to_id)
        self.message = str(user.username) + 'に申請された対戦が中止になる'


class Battle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_from = db.Column(db.Integer)
    id_to = db.Column(db.Integer)
    bet = db.Column(db.Integer)
    '''
        state=-1 not requested
        state=0 waiting
        state=1 accepted
        state=2 denied
    '''
    state = db.Column(db.Integer)

    def __init__(self, id_from, id_to, bet):
        self.id_from = id_from
        self.id_to = id_to
        self.bet = bet
        self.state = 0

    @classmethod
    def select_by_two_id(cls, id_from, id_to):
        return cls.query.filter_by(id_from=id_from, id_to=id_to).first()

    @classmethod
    def select_by_from_id(cls, id_from):
        return cls.query.filter_by(id_from=id_from).all()

    @classmethod
    def select_by_to_id(cls, id_to):
        return cls.query.filter_by(id_to=id_to).all()

    @classmethod
    def select_by_id(cls, id):
        return cls.query.filter_by(id=id).first()

    @classmethod
    def select_all(cls):
        return cls.query.all()
