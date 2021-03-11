'''
main app instance is here and also the views for the endpoints, default port is on 5000

'''


#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#


from flask import Flask, render_template, request, send_from_directory, session
# from flask.ext.sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from .utils.forms import *
import os
import werkzeug
import jinja2
from .views import bp
from flask import Flask, render_template, request
# from flask.ext.sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from .forms import *
import os
from pathlib import Path
import werkzeug
import jinja2
from .views import bp
from .oauthview import oauth_bp



def create_app(config_filename='application.config_dev'):
    
    # Definition of app

    app = Flask(__name__, static_url_path="/static", static_folder=str(Path(__file__).parent.parent)+"/static")
    app.register_blueprint(bp)
    app.register_blueprint(oauth_bp)
    app.config.from_object(config_filename)
    #db = SQLAlchemy(app)
    
    temp_loader = jinja2.ChoiceLoader([
            app.jinja_loader,
            jinja2.FileSystemLoader(['templates']),
        ])
    app.jinja_loader = temp_loader
    
    
    # Error handlers
    
    
    @app.errorhandler(werkzeug.exceptions.InternalServerError)
    def internal_error(error):
        #db_session.rollback()
        return render_template('errors/500.html', previous=session["previous"]), 500
    
    
    @app.errorhandler(werkzeug.exceptions.NotFound)
    def not_found_error(error):
        return render_template('errors/404.html', previous=session["previous"]), 404
    
    # logger
    
    if not app.debug:
        file_handler = FileHandler('error.log')
        file_handler.setFormatter(
            Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
        )
        app.logger.setLevel(logging.INFO)
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.info('errors')
    
    return app
