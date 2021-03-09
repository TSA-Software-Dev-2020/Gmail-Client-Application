import google.oauth2.credentials
import google_auth_oauthlib.flow
import os

class Auth:
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        os.path.join(os.path.dirname(__file__), 'client_secret.json'),
        scopes=['https://www.googleapis.com/auth/gmail.metadata'])


    def __init__(self):
        self.flow.redirect_uri = 'http://localhost:5000/oauth2callback'
        
        self.authorization_url, self.state = self.flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true'
        )