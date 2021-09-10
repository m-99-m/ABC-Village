from flask import (
    Flask, render_template, request, redirect, url_for, flash,
)
from models import (
    db, User, History, is_admin, get_next_needVP, HisLevelUp, HisBet, HisBet2, Battle,
    HisCancel, HisDenied, is_contest_running, HisStop0, HisStop1
)
from forms import (
    AddUserForm, UpdateUserForm, LevelUpForm, BattleRequestForm
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
    users = User.select_all()
    return render_template('users.html', users=users, form=form)


@module_juutakuti.route('/users/<username>', methods=['GET', 'POST'])
def user(username):
    form0 = LevelUpForm()
    form1 = BattleRequestForm()
    form1.type.data = -2
    forms0 = []
    forms1 = []
    user = User.select_by_username(username)
    if not user:
        return render_template('page_not_found.html')
    if user.username != username:
        return redirect(url_for('module_juutakuti.user', username=user.username))

    if current_user.is_authenticated:
        if current_user.username == user.username:
            form0 = LevelUpForm()
            needVP = get_next_needVP(current_user.level)
            form0.submit.label.text = 'LvUP 必要VP: ' + str(needVP)
            if 'submit' in request.form:
                form0 = LevelUpForm(request.form)
                if request.method == 'POST':
                    if needVP == 0:
                        flash('もはやLvは上がらないようです')
                    elif current_user.VP < needVP:
                        flash('VPが不足しています')
                    else:
                        with db.session.begin(subtransactions=True):
                            his = HisLevelUp(user.id, -needVP, user.level)
                            db.session.add(his)
                            user.level += 1
                            user.VP -= needVP
                        db.session.commit()
                        flash('LvUP!')
                    return redirect(url_for('module_juutakuti.user', username=username))
            else:
                if request.method == 'POST':
                    temp = BattleRequestForm(request.form)
                    temp.battle_id.data = temp.description.data
                    temp.type.data = max(temp.name_from.data, temp.name_to.data)
                    bt = Battle.select_by_id(temp.battle_id.data)
                    if bt:
                        if bt.id_to == current_user.id:
                            if 'submit0' in request.form:
                                with db.session.begin(subtransactions=True):
                                    bt = Battle.select_by_id(temp.battle_id.data)
                                    if not bt:
                                        flash('操作に失敗しました')
                                    elif bt.state != 0:
                                        flash('操作に失敗しました')
                                    else:
                                        if is_contest_running():
                                            flash('この操作はコンテストの処理が終わるまで許されません')
                                        elif current_user.VP < bt.bet:
                                            flash('VPが不足しています')
                                        else:
                                            bt.state = 1
                                            his = HisBet2(bt.id_to, -bt.bet, bt.id_from)
                                            db.session.add(his)
                                            current_user.VP -= bt.bet
                                            flash('申請された対戦を受けました')
                                db.session.commit()
                            else:
                                with db.session.begin(subtransactions=True):
                                    bt = Battle.select_by_id(temp.battle_id.data)
                                    if not bt:
                                        flash('操作に失敗しました')
                                    elif bt.state != 0:
                                        flash('操作に失敗しました')
                                    else:
                                        bt.state = 2
                                        flash('申請された対戦を断りました')
                                db.session.commit()
                        elif bt.id_from == current_user.id:
                            if temp.type.data == '0':
                                with db.session.begin(subtransactions=True):
                                    bt = Battle.select_by_id(temp.battle_id.data)
                                    if bt:
                                        if bt.state != 0:
                                            flash('操作に失敗しました')
                                        else:
                                            his = HisCancel(bt.id_from, bt.bet, bt.id_to)
                                            db.session.add(his)
                                            current_user.VP += bt.bet
                                            db.session.delete(bt)
                                            flash('対戦をキャンセルしました')
                                    else:
                                        flash('操作に失敗しました')
                                db.session.commit()
                            elif temp.type.data == '2':
                                with db.session.begin(subtransactions=True):
                                    bt = Battle.select_by_id(temp.battle_id.data)
                                    if bt:
                                        if bt.state != 2:
                                            flash('操作に失敗しました')
                                        else:
                                            his = HisDenied(bt.id_from, bt.bet, bt.id_to)
                                            db.session.add(his)
                                            current_user.VP += bt.bet
                                            db.session.delete(bt)
                                            flash('VPを回収しました')
                                    else:
                                        flash('操作に失敗しました')
                                db.session.commit()
                    else:
                        flash('操作に失敗しました')

            temp = Battle.select_by_to_id(current_user.id)
            for t in temp:
                f = BattleRequestForm()
                f.set(t.id_from, t.id_to)
                forms0.append(f)

            temp = Battle.select_by_from_id(current_user.id)
            for t in temp:
                f = BattleRequestForm()
                f.set(t.id_from, t.id_to)
                forms1.append(f)
        else:
            if request.method == 'POST':
                form1 = BattleRequestForm(request.form)
                form1.battle_id.data = form1.description.data
                form1.type.data = max(form1.name_from.data, form1.name_to.data)
                if form1.type.data == '-1':
                    if form1.validate():
                        with db.session.begin(subtransactions=True):
                            bt = Battle.select_by_two_id(current_user.id, user.id)
                            if bt:
                                flash('操作に失敗しました')
                            elif current_user.VP < form1.bet.data:
                                flash('VPが不足しています')
                            else:
                                if is_contest_running():
                                    flash('この操作はコンテストの処理が終わるまで許されません')
                                else:
                                    bt = Battle(current_user.id, user.id, form1.bet.data)
                                    his = HisBet(current_user.id, -form1.bet.data, user.id)
                                    db.session.add(his)
                                    db.session.add(bt)
                                    current_user.VP -= form1.bet.data
                                    flash('対戦を申請しました')
                        db.session.commit()
                elif form1.type.data == '0':
                    with db.session.begin(subtransactions=True):
                        bt = Battle.select_by_id(form1.battle_id.data)
                        if bt:
                            if bt.state != 0:
                                flash('操作に失敗しました')
                            else:
                                his = HisCancel(bt.id_from, bt.bet, bt.id_to)
                                db.session.add(his)
                                current_user.VP += bt.bet
                                db.session.delete(bt)
                                flash('対戦をキャンセルしました')
                        else:
                            flash('操作に失敗しました')
                    db.session.commit()
                elif form1.type.data == '2':
                    with db.session.begin(subtransactions=True):
                        bt = Battle.select_by_id(form1.battle_id.data)
                        if bt:
                            if bt.state != 2:
                                flash('操作に失敗しました')
                            else:
                                his = HisDenied(bt.id_from, bt.bet, bt.id_to)
                                db.session.add(his)
                                current_user.VP += bt.bet
                                db.session.delete(bt)
                                flash('VPを回収しました')
                        else:
                            flash('操作に失敗しました')
                    db.session.commit()
            form1.set(current_user.id, user.id)



    return render_template('house.html', user=User.select_by_username((username)), username=username,
                           form0=form0, form1=form1, forms0=forms0, forms1=forms1)


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


@module_juutakuti.route('/users/<username>/history', methods=['GET', 'POST'])
def history(username):
    user = User.select_by_username(username)
    if user:
        his = History.select_by_user_id(user.id)
        his.reverse()
        return render_template('history.html', username=user.username, history=his)
    else:
        return render_template('page_not_found.html')

@module_juutakuti.route('/users/battles', methods=['GET', 'POST'])
def battles():
    if is_admin():
        battles = Battle.select_all()
        bs = []
        class temp():
            id = 0
            to = 0
            fr = 0
            bet = 0
            state = 0

        for b in battles:
            t = temp()
            t.id = b.id
            t.to = User.select_by_id(b.id_to).username
            t.fr = User.select_by_id(b.id_from).username
            t.bet = b.bet
            t.state = b.state
            bs.append(t)
        return render_template('battles.html', battles=bs)
    return render_template('page_not_found.html')


@module_juutakuti.route('/battle_erase/<id>/<state>', methods=['GET', 'POST'])
def battle_delete(id, state):
    if is_admin():
        b = Battle.select_by_id(id)
        if b:
            if str(b.state) == state:
                with db.session.begin(subtransactions=True):
                    user0 = User.select_by_id(b.id_from)
                    user1 = User.select_by_id(b.id_to)
                    his = HisStop0(user0.id, b.bet, user1.id)
                    db.session.add(his)
                    user0.VP += b.bet
                    if state == '1':
                        user1.VP += b.bet
                        his = HisStop1(user1.id, b.bet, user0.id)
                        db.session.add(his)
                    db.session.delete(b)
                db.session.commit()

        return redirect(url_for('module_juutakuti.battles'))
    return render_template('page_not_found.html')