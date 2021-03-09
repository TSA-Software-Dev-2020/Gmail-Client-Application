from flask import Flask, Blueprint, render_template, request, send_from_directory, redirect
# from flask.ext.sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from .utils.forms import *
import os
import werkzeug
import jinja2
import os
from .utils import gmail_api


bp = Blueprint("bp", __name__)



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
    return render_template('pages/index.html')

@bp.route('/about')
def about():
    return render_template('pages/placeholder.about.html')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        return redirect(gmail_api.Auth().authorization_url)
    form = LoginForm(request.form)
    return render_template('forms/login.html', form=form)

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

# @bp.route('/register')
# def register():
#     form = RegisterForm(request.form)
#     return render_template('forms/register.html', form=form)


# @bp.route('/forgot')
# def forgot():
#     form = ForgotForm(request.form)
#     return render_template('forms/forgot.html', form=form)

# @bp.route('/static/css/<path:filename>')
# def static_files_css(filename):
#     return send_from_directory(app.static_folder, filename=filename)


# Error handlers.


@bp.errorhandler(werkzeug.exceptions.InternalServerError)
def internal_error(error):
    #db_session.rollback()
    return render_template('errors/500.html'), 500


@bp.errorhandler(werkzeug.exceptions.NotFound)
def not_found_error(error):
    return render_template('errors/404.html'), 404