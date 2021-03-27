from flask import Flask, Blueprint, render_template, request, send_from_directory, redirect, session
# from flask.ext.sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from .utils.forms import *
import os
import werkzeug
import jinja2
import os
from .utils.forms import LoginForm
from .utils import gmail_api


bp = Blueprint("bp", __name__)



# Automatically tear down SQLAlchemy.
'''
@app.teardown_request
def shutdown_session(exception=None):
    db_session.remove()
'''

# Login required decorator.
'''
def login_required(test):
    @wraps(test)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return test(*args, **kwargs)
        else:
            flash('You need to login first.')
            return redirect(url_for('login'))
    return wrap
'''

@bp.route('/')
def home():
    session["previous"] = "/"
    return render_template('pages/index.html')

@bp.route('/about')
def about():
    session["previous"] = "/about"
    return render_template('pages/project.html')

@bp.route('/info')
def info():
    session["previous"] = "/info"
    return render_template('pages/info.html')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm()
    session["previous"] = "/login"
    while(request.method == "POST"):
        if login_form.is_submitted and login_form.agreed.data == True:
            gmail = gmail_api.Gmail()
            session['state'] = gmail.state
            print(session['state'])
            return redirect(gmail.authorization_url)
        else:
            return "You must agree to continue"
    return render_template('forms/login.html', form=login_form)


@bp.route('/attm_download')
def attm_download():
    return "<h2>Attachment preview isn't supported nor download so far</h2>"


''''
@bp.route('/register')
def register():
    form = RegisterForm(request.form)
    return render_template('forms/register.html', form=form)
@bp.route('/forgot')
def forgot():
    form = ForgotForm(request.form)
    return render_template('forms/forgot.html', form=form)
'''

@bp.route('/static/css/<path:filename>')
def static_files_css(filename):
    return send_from_directory('../static/css/', filename=filename)

@bp.route('/static/fonts/<path:filename>')
def static_files_fonts(filename):
    return send_from_directory('../static/fonts/', filename=filename)

@bp.route('/static/ico/<path:filename>')
def static_files_icos(filename):
    return send_from_directory('../static/ico', filename=filename)

@bp.route('/static/js/<path:filename>')
def static_files_js(filename):
    return send_from_directory('../static/js/', filename=filename)


# Error handlers.