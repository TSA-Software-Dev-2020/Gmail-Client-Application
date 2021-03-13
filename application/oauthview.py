from flask import Flask, Blueprint, render_template, request, send_from_directory, redirect, session
# from flask.ext.sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from .utils.forms import *
import os
import werkzeug
import jinja2
import os
from .utils.gmail_api import Auth


oauth_bp = Blueprint("oauth_bp", __name__)

@oauth_bp.route('/oauth2callback')
def oauth2callback():
    return request.args.get('code')