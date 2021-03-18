from flask import session, jsonify
import google.oauth2.credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
# from oauth2client.clientsecrets import InvalidClientSecretsError
import google_auth_oauthlib.flow
from bs4 import BeautifulSoup
import lxml
from typing import List, Optional, Union
import os
import base64
from .label import Label
from .message import Message

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(os.path.dirname(__file__), 'service-account-creds.json')
os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'

class Gmail:
     
    _Scopes = ['https://www.googleapis.com/auth/gmail.modify', 'https://www.googleapis.com/auth/gmail.settings.basic']
    API_SERVICE = 'gmail'
    API_VERSION = 'v1'
    
    def __init__(
        self,
        state=None
    ):
        self.flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
            os.path.join(os.path.dirname(__file__), 'client_secret.json'),
            scopes=self._Scopes,
            state=state)
        self.flow.redirect_uri = 'http://localhost:5000/oauth2callback'
        
        self.authorization_url, self.state = self.flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true'
        )
    
    def get_messages(
        self,
        user_id: str = 'me',
        labels: Optional[List[Label]] = None,
        query: str = '',
        attachments: Union['ignore', 'reference', 'download'] = 'reference',
        include_spam_trash: bool = False,
        message_index:int = 0
        ):
        
        credentials = google.oauth2.credentials.Credentials(
            **session['credentials'])
        with build(self.API_SERVICE, self.API_VERSION, credentials=credentials) as service:
            if labels is None:
                labels = []
            labels_ids = [
                lbl.id if isinstance(lbl, Label) else lbl for lbl in labels
            ]
            res = service.users().messages().list(
                userId=user_id,
                q=query,
                labelIds=labels_ids
            ).execute()
            message_refs = []
            if 'messages' in res:
                message_refs.extend(res['messages'])

            return self._build_message_from_ref(user_id='me', message_ref=message_refs[message_index])

    def list_labels(self, user_id: str = 'me') -> List[Label]:

        
        try:
            credentials = google.oauth2.credentials.Credentials(
                **session['credentials'])
            with build(self.API_SERVICE, self.API_VERSION, credentials=credentials) as service:
                res = service.users().labels().list(
                    userId=user_id
                ).execute()

        except HttpError as error:
            # Pass along the error
            raise error

        else:
            labels = [Label(name=x['name'], id=x['id']) for x in res['labels']]
            return labels

    def _build_message_from_ref(
        self,
        user_id: str,
        message_ref: dict,
        attachments: Union['ignore', 'reference', 'download'] = 'reference',
    ) -> Message or HttpError:

        try:
            # Get message JSON
            credentials = google.oauth2.credentials.Credentials(
                **session['credentials'])
            with build(self.API_SERVICE, self.API_VERSION, credentials=credentials) as service:
                message = service.users().messages().get(
                    userId=user_id, id=message_ref['id']
                ).execute()
        
        except HttpError as error:
            # Pass along the error
            print(error)
            return error

        else:
            msg_id = message['id']
            thread_id = message['threadId']
            label_ids = []
            if 'labelIds' in message:
                user_labels = {x.id: x for x in self.list_labels(user_id=user_id)}
                label_ids = [user_labels[x] for x in message['labelIds']]

            payload = message['payload']
            headers = payload['headers']

            # Get header fields (date, from, to, subject)
            date = ''
            sender = ''
            recipient = ''
            subject = ''
            for hdr in headers:
                if hdr['name'] == 'Date':
                    try:
                        date = str(parser.parse(hdr['value']).astimezone())
                    except Exception:
                        date = hdr['value']
                elif hdr['name'] == 'From':
                    sender = hdr['value']
                elif hdr['name'] == 'To':
                    recipient = hdr['value']
                elif hdr['name'] == 'Subject':
                    subject = hdr['value']
            
            parts = self._evaluate_message_payload(
                payload, user_id, message_ref['id'], attachments
            )

            plain_msg = None
            html_msg = None
            attms = []
            for part in parts:
                if part['part_type'] == 'plain':
                    if plain_msg is None:
                        plain_msg = part['body']
                    else:
                        plain_msg += '\n' + part['body']
                elif part['part_type'] == 'html':
                    if html_msg is None:
                        html_msg = part['body']
                    else:
                        html_msg += '<br/>' + part['body']
                elif part['part_type'] == 'attachment':
                    attm = Attachment(self.service, user_id, msg_id,
                                      part['attachment_id'], part['filename'],
                                      part['filetype'], part['data'])
                    attms.append(attm)

            credentials = google.oauth2.credentials.Credentials(
                **session['credentials'])
            with build(self.API_SERVICE, self.API_VERSION, credentials=credentials) as service:
                return Message(service, user_id, msg_id, thread_id, recipient, 
                    sender, subject, date, None, plain_msg, html_msg, label_ids,
                    attms)


    def _evaluate_message_payload(
        self,
        payload: dict,
        user_id: str,
        msg_id: str,
        attachments: Union['ignore', 'reference', 'download'] = 'reference'
    ) ->List[dict]:

        if 'attachmentId' in payload['body']:  # if it's an attachment
            if attachments == 'ignore':
                return []

            att_id = payload['body']['attachmentId']
            filename = payload['filename']
            if not filename:
                filename = 'unknown'

            obj = {
                'part_type': 'attachment',
                'filetype': payload['mimeType'],
                'filename': filename,
                'attachment_id': att_id,
                'data': None
            }

            if attachments == 'reference':
                return [obj]
            
            else:  # attachments == 'download'
                if 'data' in payload['body']:
                    data = payload['body']['data']
                else:
                    res = self.service.users().messages().attachments().get(
                        userId=user_id, messageId=msg_id, id=att_id
                    ).execute()
                    data = res['data']

                file_data = base64.urlsafe_b64decode(data)
                obj['data'] = file_data
                return [obj]
        
        elif payload['mimeType'] == 'text/html':
            data = payload['body']['data']
            data = base64.urlsafe_b64decode(data)
            body = BeautifulSoup(data, 'lxml', from_encoding='utf-8').body
            return [{ 'part_type': 'html', 'body': str(body) }]

        elif payload['mimeType'] == 'text/plain':
            data = payload['body']['data']
            data = base64.urlsafe_b64decode(data)
            body = data.decode('UTF-8')
            return [{ 'part_type': 'plain', 'body': body }]

        elif payload['mimeType'].startswith('multipart'):
            ret = []
            if 'parts' in payload:
                for part in payload['parts']:
                    ret.extend(self._evaluate_message_payload(part, user_id, msg_id,
                                                              attachments))
            return ret

        return []
