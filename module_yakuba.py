from flask import (
    Flask, render_template, request, redirect, url_for, flash,
)
from datetime import datetime
from models import db, User, Contest, is_admin, get_needVP, HisContestWin, Battle, HisDenied, HisBattleResult
from forms import (
    AddContestForm, UpdateContestForm
)
import json
from flask import Blueprint
module_yakuba = Blueprint('module_yakuba', __name__)


@module_yakuba.route('/contests', methods=['GET', 'POST'])
def contests():
    form = AddContestForm(request.form)

    if is_admin():
        if request.method == 'POST' and form.validate():
            sd = form.startDate.data
            st = form.startTime.data
            dt = datetime(year=sd.year, month=sd.month, day=sd.day, hour=st.hour, minute=st.minute, second=st.second)
            index = form.index.data
            contest = Contest(index, dt)
            with db.session.begin(subtransactions=True):
                db.session.add(contest)
            db.session.commit()

    contests = Contest.get_contests_info()
    return render_template('contests.html', contests=contests, form=form)


@module_yakuba.route('/contests/erase/<index>', methods=['GET', 'POST'])
def contest_erase(index):
    if is_admin():
        contest = Contest.select_by_index(index)
        if contest:
            with db.session.begin(subtransactions=True):
                db.session.delete(contest)
            db.session.commit()
        return redirect(url_for('module_yakuba.contests'))
    else:
        return render_template('page_not_found.html')


@module_yakuba.route('/contests/update/<index>', methods=['GET', 'POST'])
def contest_update(index):
    if is_admin():
        contest = Contest.select_by_index(index)
        if contest:
            form = UpdateContestForm(request.form)
            form.index.data = index
            if request.method == 'POST' and form.validate():
                users = User.select_all()
                users = [u for u in users if (u.register_time - contest.starttime).total_seconds() < 0]
                f = request.files[form.json.name]
                js = json.load(f)
                ranks = {}
                scores = {}
                worstRank = js[-1]["Rank"]
                for user in users:
                    ranks[user.username] = worstRank
                    scores[user.username] = 0
                for item in js:
                    if ranks.get(item["UserScreenName"]):
                        ranks[item["UserScreenName"]] = item["Rank"]
                        scores[item["UserScreenName"]] = item["TotalResult"]["Score"] // 100

                battles = Battle.select_all()
                nb = []
                for b in battles:
                    if b.state == 1:
                        nb.append(b)
                    else:
                        with db.session.begin(subtransactions=True):
                            bt = Battle.select_by_id(b.id)
                            if bt:
                                his = HisDenied(bt.id_from, bt.bet, bt.id_to)
                                db.session.add(his)
                                User.select_by_id(bt.id_from).VP += bt.bet
                                db.session.delete(bt)
                        db.session.commit()

                with db.session.begin(subtransactions=True):
                    for k, v in ranks.items():
                        user = User.select_by_username(k)
                        if v == 1:
                            user.champion_medal += 1
                        if scores[k] == 3200:
                            user.complete_medal += 1
                        incremental = scores[k] + (user.complete_medal + user.champion_medal) * (scores[k]//100)
                        user.VP += incremental
                        his = HisContestWin(user.id, incremental, contest.index, v, scores[k])
                        db.session.add(his)

                    for b in nb:
                        u0 = b.id_from
                        u1 = b.id_to
                        n0 = User.select_by_id(u0)
                        n1 = User.select_by_id(u1)
                        if ranks[n0.username] < ranks[n1.username]:
                            his = HisBattleResult(u0, b.bet*2, contest.index, u1, 1, 1, b.bet)
                            db.session.add(his)
                            his = HisBattleResult(u1, 0, contest.index, u0, 0, -1, b.bet)
                            db.session.add(his)
                            n0.VP += b.bet*2
                        elif ranks[n0.username] == ranks[n1.username]:
                            his = HisBattleResult(u0, b.bet, contest.index, u1, 1, 0, b.bet)
                            db.session.add(his)
                            his = HisBattleResult(u1, b.bet, contest.index, u0, 0, 0, b.bet)
                            db.session.add(his)
                            n0.VP += b.bet
                        else:
                            his = HisBattleResult(u0, 0, contest.index, u1, 1, -1, b.bet)
                            db.session.add(his)
                            his = HisBattleResult(u1, b.bet*2, contest.index, u0, 0, 1, b.bet)
                            db.session.add(his)
                            n1.VP += b.bet*2
                        db.session.delete(b)
                    db.session.delete(contest)

                db.session.commit()

                return redirect(url_for('module_yakuba.contests'))
            return render_template('updatecontest.html', form=form)

    return render_template('page_not_found.html')

@module_yakuba.route('/documents', methods=['GET', 'POST'])
def documents():
    return render_template('documents.html')

@module_yakuba.route('/documents/<document>', methods=['GET', 'POST'])
def document(document):
    if document == 'doc_needVP':
        return render_template(document + '.html', value=get_needVP())

    else:
        l = ["doc_ifBlue", "doc_ruleABC", "doc_ruleBattle"]
        if document in l:
            return render_template(document + '.html')
        else:
            return render_template('page_not_found.html')
