from flask import (
    Flask, render_template, request, redirect, url_for, flash,
)
from models import Post, User, db
from flask import Blueprint
from forms import PostForm
module_hiroba = Blueprint('module_hiroba', __name__)
from flask_login import current_user
from flask import Markup

@module_hiroba.route('/bbs', methods=['GET', 'POST'])
def bbs():

    posts = []

    p = Post.select_all()

    for post in p:
        u = User.select_by_id(post.user_id)
        temp = {"id":post.id,
                "username": u.username,
                "level": post.level,
                "post_time": post.post_time,
                "messages": post.message.split('\n')
                }
        posts.append(temp)

    form = PostForm(request.form)

    if request.method == 'POST' and form.validate() and current_user.is_authenticated:
        p = Post(current_user.id, form.message.data, current_user.level)
        with db.session.begin(subtransactions=True):
            db.session.add(p)
            flash('投稿しました')
        db.session.commit()

        return redirect(url_for('module_hiroba.bbs'))

    return render_template('bbs.html', posts=posts, form=form)
    #return render_template('page_not_found.html')
