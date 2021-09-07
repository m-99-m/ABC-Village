from flask import (
    Flask, render_template, request, redirect, url_for, flash,
)
from models import db, User, is_admin, get_next_needVP
from forms import (
    AddUserForm, UpdateUserForm, LevelUpForm
)
from flask_login import current_user
from flask import Blueprint
module_juutakuti = Blueprint('module_juutakuti', __name__)

@module_juutakuti.route('/users', methods=['GET', 'POST'])
def users():
    form = AddUserForm(request.form)
    if is_admin():
        if request.method == 'POST' and form.validate():
            user = User(form.username.data, form.password.data)
            with db.session.begin(subtransactions=True):
                db.session.add(user)
            db.session.commit()
    users = User.get_ranking_info()
    return render_template('users.html', users=users, form=form)


@module_juutakuti.route('/users/<username>', methods=['GET', 'POST'])
def user(username):
    form = LevelUpForm(request.form)
    if current_user.is_authenticated and current_user.username == username:
        needVP = get_next_needVP(current_user.level)
        form.submit.label.text = 'LvUP 必要VP: ' + str(needVP)
        if request.method == 'POST':
            if needVP == 0:
                flash('もはやLvは上がらないようだ')
            elif current_user.VP < needVP:
                flash('VPが不足しています')
            else:
                with db.session.begin(subtransactions=True):
                    user = User.select_by_username(current_user.username)
                    user.level += 1
                    user.VP -= needVP
                db.session.commit()
                flash('LvUP!')
            return redirect(url_for('module_juutakuti.user', username=username))
    return render_template('house.html', user=User.select_by_username((username)), username=username, form=form)


@module_juutakuti.route('/users/<username>/update', methods=['GET', 'POST'])
def user_update(username):
    if is_admin():
        user = User.select_by_username(username)
        if user:
            form = UpdateUserForm(request.form, user)
            if form.username.data == '':
                form.username.data = user.username
                form.VP.data = user.VP
                form.level.data = user.level
                form.register_time.data = user.register_time
            if request.method == 'POST' and (form.username.data == user.username or form.validate()):
                with db.session.begin(subtransactions=True):
                    user.username = form.username.data
                    user.VP = form.VP.data
                    user.level = form.level.data
                    user.register_time = form.register_time.data
                    user.inner_username = user.username.lower()
                db.session.commit()
                return redirect(url_for('module_juutakuti.users'))
            return render_template('update_user.html', form=form)

    return render_template('page_not_found.html')
