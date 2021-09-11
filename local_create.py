from flask import (
    Flask, render_template, request, redirect, url_for, flash,
)
from flask_login import login_required, login_user, logout_user, current_user
from datetime import datetime
from app import app
from models import db, User
from forms import (
    LoginForm, RegisterForm
)
from flask_migrate import Migrate
import secrets
from flask_bcrypt import generate_password_hash
#db.drop_all()
db.create_all()
'''
from sqlite3 import connect, Row

db = connect('test.sqlite')
'''
#db.execute('alter table User add  special_medal int default 0 ;')
'''
user = User('m_99', 'password')
db.session.add(user)
db.session.commit()
'''