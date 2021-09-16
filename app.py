from flask import (
    Flask, render_template, request, redirect, url_for, flash, 
)

app = Flask(__name__)

from module_basis import module_basis
from module_regi import module_regi
from module_juutakuti import module_juutakuti
from module_yakuba import module_yakuba
from module_hiroba import module_hiroba

app.register_blueprint(module_basis)
app.register_blueprint(module_regi)
app.register_blueprint(module_juutakuti)
app.register_blueprint(module_yakuba)
app.register_blueprint(module_hiroba)

@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html')







