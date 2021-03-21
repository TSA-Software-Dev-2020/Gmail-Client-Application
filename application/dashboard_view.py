from flask import Flask, Blueprint, render_template, request, send_from_directory, redirect, session
import google.oauth2.credentials
# from flask.ext.sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from .utils.forms import *
import os
import werkzeug
import requests
import jinja2
import threading 
import math
import os
from .utils.gmail_api import Gmail
from .utils import label
from .utils.label import Label
from .utils.forms import ComposeForm

db_bp = Blueprint("db_bp", __name__)

@db_bp.route('/dashboard')
def dashboard():
    if "credentials" not in session:
        return redirect("/")
    form = ComposeForm()
    gmail = Gmail(creds=session["credentials"])
    # You can also specify message_index= to get a singular message.
    inbox_messages = None
    sent_messages = None
    draft_messages = None
    if request.args.get("tab") == "inbox":
        session["previous"] = "/dashboard?tab=inbox"
        unread_inbox_messages = gmail.get_unread_inbox()
        inbox_messages = gmail.get_inbox()
        return render_template("pages/inbox.dashboard.html", user_metadata=gmail.user_metadata, inbox=inbox_messages, form=form)
    elif request.args.get("tab") == "sents":
        session["previous"] = "/dashboard?tab=sents"
        sent_messages = gmail.get_sents()
        return render_template("pages/sent.dashboard.html", user_metadata=gmail.user_metadata, sents=sent_messages, form=form)
    elif request.args.get("tab") == "drafts":
        session["previous"] = "/dashboard?tab=drafts"
        draft_messages = gmail.get_drafts()
        return render_template("pages/draft.dashboard.html", user_metadata=gmail.user_metadata, drafts=draft_messages, form=form)    
    return redirect("/dashboard?tab=inbox")


@db_bp.route('/dashboard/message_submit', methods=['GET', 'POST'])
def message_submit():
    form = ComposeForm()
    if request.method == "POST":
        msg = {
            "to": str(form.recipient.data),
            "sender": "me",
            "subject": str(form.subject.data),
            "msg_plain": str(form.body.data)
        }
        gmail = Gmail(creds=session["credentials"])
        sent_msg = gmail.send_message(**msg)
    return redirect(session["previous"])


@db_bp.route('/revoke')
def revoke():
    if 'credentials' not in session:
        return 
     
    credentials = google.oauth2.credentials.Credentials(
        **session['credentials'])
     
    revoke = requests.post('https://oauth2.googleapis.com/revoke',
        params={'token': credentials.token},
        headers = {'content-type': 'application/x-www-form-urlencoded'})
     
    status_code = revoke.status_code
    return redirect("/clear")


@db_bp.route('/clear')
def clear_credentials():
    if 'credentials' in session:
        del session['credentials']
    return redirect("/")