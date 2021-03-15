from flask import session
import google.oauth2.credentials
from googleapiclient.discovery import build
# from oauth2client.clientsecrets import InvalidClientSecretsError
import google_auth_oauthlib.flow
from typing import Union, Optional
import os

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(os.path.dirname(__file__), 'service-account-creds.json')

class Gmail:
     
    _Scopes = ['https://www.googleapis.com/auth/gmail.metadata', 'email']
    API_SERVICE = 'gmail'
    API_VERSION = 'v1'
    
    def __init__(self):
        self.flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
            os.path.join(os.path.dirname(__file__), 'client_secret.json'),
            scopes=self._Scopes)
        self.flow.redirect_uri = 'http://localhost:5000/oauth2callback'
        
        self.authorization_url, self.state = self.flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true'
        )
    
    def get_stuff(self):
        credentials = google.oauth2.credentials.Credentials(
            **flask.session['credentials'])
        with build(self.API_SERVICE, self.API_VERSION, credentials=credentials) as service:
            response = service.users().messages().list(userId='me').execute()
            return flask.jsonify(response)