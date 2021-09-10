from flask import (
    Flask, render_template, request, redirect, url_for, flash,
)
from flask_login import login_required, login_user, logout_user, current_user
from models import db, User
from forms import (
    LoginForm, RegisterForm
)
import secrets
from flask_bcrypt import generate_password_hash
from flask import Blueprint
module_regi = Blueprint('module_regi', __name__)

@module_regi.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        username = form.username.data
        password = form.password.data
        user = User.select_by_username(username)
        if user and user.check_password(password):
            """ ユーザに対してログイン処理を施す """
            login_user(user)
            return redirect(url_for('module_juutakuti.user', username=user.username))
        elif user:
            flash('パスワードが間違っています')
        else:
            flash('その人はABC村の住民ではありません')
    return render_template('login.html', form=form)


@module_regi.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if form.val_str.data == '':
        form.val_str.data = secrets.token_hex(255)
        form.val_hash.data = generate_password_hash(form.val_str.data).decode('utf-8')

    if request.method == 'POST' and form.validate():
        if form.check_token() == 1:
            username = form.username.data
            password = form.password.data
            user = User(username, password)
            f = True
            with db.session.begin(subtransactions=True):
                if form.validate():
                    db.session.add(user)
                else:
                    f = False
            db.session.commit()
            if f:
                login_user(user)
                return redirect(url_for('module_juutakuti.user', username=user.username))
        else:
            flash('認証に失敗しました')

    return render_template('register.html', form=form)

@module_regi.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('module_basis.home'))
