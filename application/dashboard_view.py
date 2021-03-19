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
from .utils import label
from .utils.label import Label

db_bp = Blueprint("db_bp", __name__)

@db_bp.route('/dashboard')
def dashboard():
    gmail = Gmail(creds=session["credentials"])

    # You can also specify message_index= to get a singular message.
    stuff = None
    if request.args.get("tab") == "inbox":
        stuff = gmail.get_messages(labels=[label.INBOX])
    return str(stuff)