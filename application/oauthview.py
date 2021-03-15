from flask import Flask, Blueprint, render_template, request, send_from_directory, redirect, session
# from flask.ext.sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from .utils.forms import *
import os
import werkzeug
import jinja2
import os
from .utils.gmail_api import Gmail


oauth_bp = Blueprint("oauth_bp", __name__)

@oauth_bp.route('/oauth2callback')
def oauth2callback():
    state = session['state']
    gmail = Gmail(state=state)
    authorization_response = request.url
    gmail.flow.fetch_token(authorization_response=authorization_response)
    credentials = gmail.flow.credentials
    session['credentials'] = {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
        }
    stuff = gmail.get_stuff()
    return str(stuff)