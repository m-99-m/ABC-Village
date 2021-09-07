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

import secrets
from flask_bcrypt import generate_password_hash
db.create_all()