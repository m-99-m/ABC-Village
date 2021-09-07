from flask import (
    Flask, render_template, request, redirect, url_for, flash,
)
from datetime import datetime
from models import db, User, Contest, is_admin, get_needVP
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
                f = request.files[form.json.name]
                js = json.load(f)

                with db.session.begin(subtransactions=True):
                    db.session.delete(contest)
                    for item in js:
                        user = User.select_by_username(item["UserName"])
                        if user:
                            user.VP += item["TotalResult"]["Score"] // 100
                db.session.commit()

                return redirect(url_for('module_yakuba.contests'))
            return render_template('updatecontest.html', form=form)

    return render_template('page_not_found.html')

@module_yakuba.route('/documents', methods=['GET', 'POST'])
def documents():
    return render_template('documents.html')

@module_yakuba.route('/documents/<document>', methods=['GET', 'POST'])
def document(document):
    return render_template(document + '.html', value=get_needVP())