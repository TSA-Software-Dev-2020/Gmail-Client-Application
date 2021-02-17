'''
main app instance is here and also the views for the endpoints, default port is on 5000

'''


#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#


from flask import Flask, render_template, request, send_from_directory
# from flask.ext.sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from .utils.forms import *
import os
import werkzeug
import jinja2
from .views import bp
=======
from flask import Flask, render_template, request
# from flask.ext.sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from .forms import *
import os
import werkzeug
import jinja2


#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
app.config.from_object('application.config_dev')
#db = SQLAlchemy(app)

temp_loader = jinja2.ChoiceLoader([
        app.jinja_loader,
        jinja2.FileSystemLoader(['templates']),
    ])
app.jinja_loader = temp_loader

<<<<<<< HEAD
app.register_blueprint(bp)

=======
>>>>>>> 8210f62... changes
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
#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


<<<<<<< HEAD
# @app.route('/')
# def home():
#     return render_template('pages/index.html')

# @app.route('/about')
# def about():
#     return render_template('pages/placeholder.about.html')


# @app.route('/login')
# def login():
#     form = LoginForm(request.form)
#     return render_template('forms/login.html', form=form)


# @app.route('/register')
# def register():
#     form = RegisterForm(request.form)
#     return render_template('forms/register.html', form=form)


# @app.route('/forgot')
# def forgot():
#     form = ForgotForm(request.form)
#     return render_template('forms/forgot.html', form=form)

# @app.route('/static/css/<path:filename>')
# def static_files_css(filename):
#     return send_from_directory(app.static_folder, filename=filename)

=======
@app.route('/')
def home():
    return render_template('pages/index.html')


@app.route('/about')
def about():
    return render_template('pages/placeholder.about.html')


@app.route('/login')
def login():
    form = LoginForm(request.form)
    return render_template('forms/login.html', form=form)


@app.route('/register')
def register():
    form = RegisterForm(request.form)
    return render_template('forms/register.html', form=form)


@app.route('/forgot')
def forgot():
    form = ForgotForm(request.form)
    return render_template('forms/forgot.html', form=form)
>>>>>>> 8210f62... changes

# Error handlers.


<<<<<<< HEAD
# @app.errorhandler(werkzeug.exceptions.InternalServerError)
# def internal_error(error):
#     #db_session.rollback()
#     return render_template('errors/500.html'), 500


# @app.errorhandler(werkzeug.exceptions.NotFound)
# def not_found_error(error):
#     return render_template('errors/404.html'), 404

# if not app.debug:
#     file_handler = FileHandler('error.log')
#     file_handler.setFormatter(
#         Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
#     )
#     app.logger.setLevel(logging.INFO)
#     file_handler.setLevel(logging.INFO)
#     app.logger.addHandler(file_handler)
#     app.logger.info('errors')
=======
@app.errorhandler(werkzeug.exceptions.InternalServerError)
def internal_error(error):
    #db_session.rollback()
    return render_template('errors/500.html'), 500


@app.errorhandler(werkzeug.exceptions.NotFound)
def not_found_error(error):
    return render_template('errors/404.html'), 404

if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')
>>>>>>> 8210f62... changes

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

def run_app(port_num:int=5000):
    port = int(os.environ.get('PORT', port_num))
    app.run(host='0.0.0.0', port=port)