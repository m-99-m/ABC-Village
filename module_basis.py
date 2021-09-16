from flask import (
    Flask, render_template, request, redirect, url_for, flash,
)
from flask import Blueprint
module_basis = Blueprint('module_basis', __name__)

@module_basis.route('/', methods=['GET'])
def home():
    return render_template('home.html')
