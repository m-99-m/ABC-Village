from flask import (
    Flask, render_template, request, redirect, url_for, flash,
)
from flask import Blueprint
module_hiroba = Blueprint('module_hiroba', __name__)

@module_hiroba.route('/bbs', methods=['GET', 'POST'])
def bbs():
    #return render_template('bbs.html')
    return render_template('page_not_found.html.html')
