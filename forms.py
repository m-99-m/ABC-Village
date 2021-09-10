from wtforms.form import Form
from wtforms.fields import (
    IntegerField, StringField, TextField, TextAreaField, PasswordField,
    HiddenField, SubmitField, FileField, DateTimeField
)
from wtforms.fields.html5 import DateField, TimeField
from wtforms.validators import DataRequired, EqualTo, Regexp, Length
from wtforms import ValidationError
from models import User, Contest, Battle
from AtCoder import get_highest, check_token
from flask_bcrypt import generate_password_hash, check_password_hash
from flask_login import current_user
from datetime import datetime
from flask import flash


class LoginForm(Form):
    username = StringField('名前', validators=[DataRequired()])
    password = PasswordField('パスワード', validators=[DataRequired()])
    submit = SubmitField('帰村')


class RegisterForm(Form):
    username = StringField('名前(最高レート2400以上のAtCoder ID)', validators=[DataRequired(), Regexp('^[_0-9a-zA-Z]+$', message='AtCoder IDに使われない文字が含まれています')])
    password = PasswordField('パスワード(半角英数字8～50文字)', validators=[DataRequired(), Regexp('^[_0-9a-zA-Z]+$', message='使用できない文字が含まれています'), Length(min=8, max=50, message='文字数が要求を満たしていません')])
    conf_password = PasswordField('確認用パスワード', validators=[DataRequired(), EqualTo('password', message='元のパスワードと一致しません')])
    val_str = HiddenField(label='')
    val_hash = HiddenField(label='')
    submit = SubmitField('入村')

    def validate_username(self, field):
        if User.select_by_username(field.data):
            raise ValidationError('その人はすでにABC村にいます')
        elif get_highest(field.data) < 2400:
            raise ValidationError('その人はレートが2400に満たないか、そもそも存在しません')

    def check_token(self):
        #flash(self.val_hash)
        if check_password_hash(self.val_hash.data, self.val_str.data):
            return check_token(self.username.data, self.val_hash.data)
        return 0

class AddContestForm(Form):
    index = IntegerField('番号', validators=[DataRequired()])
    startDate = DateField('開始日')
    dt = datetime.now()
    dt = dt.replace(hour=21, minute=0, second=0, microsecond=0)
    startTime = TimeField('開始時刻', default=dt)
    submit = SubmitField('追加')

    def validate_index(self, field):
        if Contest.select_by_index(field.data):
            raise ValidationError('そのコンテストはすでに追加されています')

class AddUserForm(Form):
    username = StringField('名前',
                           validators=[DataRequired(), Regexp('^[_0-9a-zA-Z]+$', message='AtCoder IDに使われない文字が含まれています')])
    password = PasswordField('パスワード(半角英数字8～50文字)',
                             validators=[DataRequired(), Regexp('^[_0-9a-zA-Z]+$', message='使用できない文字が含まれています'),
                                         Length(min=8, max=50, message='文字数が要求を満たしていません')])

    submit = SubmitField('追加')

    def validate_username(self, field):
        if User.select_by_username(field.data):
            raise ValidationError('その人はすでにABC村にいます')


class UpdateContestForm(Form):
    json = FileField('jsonファイル')
    submit = SubmitField('追加')
    index = HiddenField(label='')


class UpdateUserForm(Form):
    username = StringField('名前(最高レート2400以上のAtCoder ID)', default='',
                           validators=[DataRequired(), Regexp('^[_0-9a-zA-Z]+$', message='AtCoder IDに使われない文字が含まれています')])
    VP = IntegerField(validators=[DataRequired()])
    level = IntegerField(validators=[DataRequired()])
    register_time = DateTimeField(validators=[DataRequired()])
    submit = SubmitField('更新')

    def validate_username(self, field):
        if User.select_by_username(field.data):
            raise ValidationError('その人はすでにABC村にいます')


class LevelUpForm(Form):
    submit = SubmitField('')


class BattleRequestForm(Form):
    type = HiddenField(label='', default=-1)
    name_from = HiddenField(label='')
    name_to = HiddenField(label='')
    battle_id = HiddenField(label='', default=-1)
    description = HiddenField(label='')
    bet = IntegerField(label='1以上の整数を入力', validators=[DataRequired(message='1以上の整数を入力してください')])
    submit0 = SubmitField('')
    submit1 = SubmitField('')

    def set(self, id_from, id_to):
        self.id_from = id_from
        self.id_to = id_to
        self.name_from.label = User.select_by_id(id_from).username
        self.name_to.label = User.select_by_id(id_to).username
        bt = Battle.select_by_two_id(id_from, id_to)
        if bt:
            self.type.data = bt.state
            self.bet.data = bt.bet
            self.battle_id.data = bt.id
        else:
            self.type.data = -1
        s = self.type.data
        if current_user.id == id_from:
            if s == -1:
                self.description.label.text = ''
                self.submit0.label.text = '申請'
                self.description.label.text = '未申請'
            if s == 0:
                self.description.label.text = '返事を待っています'
                self.submit0.label.text = '取消'
            if s == 1:
                self.description.label.text = '成立しました'
            if s == 2:
                self.description.label.text = '断られました'
                self.submit0.label.text = 'VP回収'
        else:
            if s == -1:
                pass
            if s == 0:
                self.description.label = '返事を待っています'
                self.submit0.label.text = '受ける'
                self.submit1.label.text = '断る'
            if s == 1:
                self.description.label = '成立しました'
            if s == 2:
                pass
        self.name_from.data = self.type.data
        self.name_to.data = self.type.data
        self.description.data = self.battle_id.data

    def validate_bet(self, field):
        if field.data <= 0:
            raise ValidationError('1以上の整数を入力してください')

