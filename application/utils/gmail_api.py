from flask import session, jsonify
import google.oauth2.credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
# from oauth2client.clientsecrets import InvalidClientSecretsError
import google_auth_oauthlib.flow
from bs4 import BeautifulSoup
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import lxml
import html
from typing import List, Optional, Union
import math
import threading
import os
import base64
from .label import Label
from ..utils import label
from .message import Message
from .attachment import Attachment

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(os.path.dirname(__file__), 'service-account-creds.json')
os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'

class Gmail:
     
    _Scopes = ['https://www.googleapis.com/auth/gmail.modify', 'https://www.googleapis.com/auth/gmail.settings.basic']
    API_SERVICE = 'gmail'
    API_VERSION = 'v1'
    
    def __init__(
        self,
        creds=None,
        state=None,
        user_id='me'
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
        self.creds = creds
        if creds == None:
            self.credentials = None
        else:
            self.credentials = google.oauth2.credentials.Credentials(
                **creds)

        self.user_metadata = None

        if creds != None:
            with build(self.API_SERVICE, self.API_VERSION, credentials=self.credentials) as service:     
                self.user_metadata = service.users().getProfile(
                    userId=user_id
                ).execute()
    

    def send_message(
        self,
        sender: str,
        to: str,
        subject: str = '',
        msg_html: Optional[str] = None, 
        msg_plain: Optional[str] = None,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
        attachments: Optional[List[str]] = None,
        signature: bool = False,
        user_id: str = 'me'
    ) -> Message:

        msg = self._create_message(
            sender, to, subject, msg_html, msg_plain, cc=cc, bcc=bcc,
            attachments=attachments, signature=signature
        )

        try:
            res = None
            with build(self.API_SERVICE, self.API_VERSION, credentials=self.credentials) as service:
                res = service.users().messages().send(userId='me', body=msg).execute()
            return self._build_message_from_ref(user_id, res, 'reference')

        except HttpError as error:
            # Pass along the error
            raise error


    def get_inbox(
        self,
        user_id: str = 'me',
        labels: Optional[List[Label]] = None,
        query: str = '',
        attachments: Union['ignore', 'reference', 'download'] = 'reference'
    ) -> List[Message]:

        if labels is None:
            labels = []

        labels.append(label.INBOX)
        return self.get_messages(user_id, labels, query)

    def get_unread_inbox(
        self,
        user_id: str = 'me',
        labels: Optional[List[Label]] = None,
        query: str = '',
        attachments: Union['ignore', 'reference', 'download'] = 'reference'
    ) -> List[Message]:

        if labels is None:
            labels = []

        labels.append(label.INBOX)
        return self.get_unread_messages(user_id, labels, query)

    def get_unread_messages(
        self,
        user_id: str = 'me',
        labels: Optional[List[Label]] = None,
        query: str = '',
        attachments: Union['ignore', 'reference', 'download'] = 'reference',
        include_spam_trash: bool = False
    ) -> List[Message]:
        
        if labels is None:
            labels = []

        labels.append(label.UNREAD)
        return self.get_messages(user_id, labels, query, attachments,
                                 include_spam_trash)


    def get_sents(
        self,
        user_id: str = 'me',
        labels: Optional[List[Label]] = None,
        query: str = '',
        attachments: Union['ignore', 'reference', 'download'] = 'reference',
        include_spam_trash: bool = False
    ) -> List[Message]:

        if labels is None:
            labels = []

        labels.append(label.SENT)
        return self.get_messages(user_id, labels, query, attachments,
                                 include_spam_trash)

    def get_drafts(
        self,
        user_id: str = 'me',
        labels: Optional[List[Label]] = None,
        query: str = '',
        attachments: Union['ignore', 'reference', 'download'] = 'reference'
    ) -> List[Message]:

        if labels is None:
            labels = []

        labels.append(label.DRAFT)
        return self.get_messages(user_id, labels, query)


    def get_starred(
        self,
        user_id: str = 'me',
        labels: Optional[List[Label]] = None,
        query: str = '',
        attachments: Union['ignore', 'reference', 'download'] = 'reference'
    ) -> List[Message]:

        if labels is None:
            labels = []

        labels.append(label.STARRED)
        return self.get_messages(user_id, labels, query)


    def get_trash(
        self,
        user_id: str = 'me',
        labels: Optional[List[Label]] = None,
        query: str = '',
        attachments: Union['ignore', 'reference', 'download'] = 'reference'
    ) -> List[Message]:

        if labels is None:
            labels = []

        labels.append(label.TRASH)
        return self.get_messages(user_id, labels, query)


    def get_singular_message(
        self,
        msg_id:str,
        user_id: str = 'me',
        query: str = '',
        attachments: Union['ignore', 'reference', 'download'] = 'reference',
        include_spam_trash: bool = False,
        message_index:int = None
        ):

        try:

            item_0 = {
                "id": msg_id
            }

            message_refs = []
            message_refs.extend(item_0)

            return self._get_messages_from_refs(user_id, message_refs,
                                                attachments)
        except HttpError as error:
            raise error


    def get_messages(
        self,
        user_id: str = 'me',
        labels: Optional[List[Label]] = None,
        query: str = '',
        attachments: Union['ignore', 'reference', 'download'] = 'reference',
        include_spam_trash: bool = False,
        message_index:int = None
        ):

        if labels == None:
            labels = []
        labels_ids = [
            lbl.id if isinstance(lbl, Label) else lbl for lbl in labels
        ]

        try:
            with build(self.API_SERVICE, self.API_VERSION, credentials=self.credentials) as service:

                res = service.users().messages().list(
                    userId=user_id,
                    q=query,
                    labelIds=labels_ids
                ).execute()
                
                message_refs = []
                
                if 'messages' in res:
                    message_refs.extend(res['messages'])
                
                while 'nextPageToken' in res:
                    page_token = res['nextPageToken']
                    res = service.users().messages().list(
                        userId=user_id,
                        q=query,
                        labelIds=labels_ids,
                        pageToken=page_token
                    ).execute()
                    message_refs.extend(res['messages'])

            return self._get_messages_from_refs(user_id, message_refs,
                                                attachments)
        except HttpError as error:
            raise error

    def list_labels(self, user_id: str = 'me') -> List[Label]:

        
        try:
            with build(self.API_SERVICE, self.API_VERSION, credentials=self.credentials) as service:
                res = service.users().labels().list(
                    userId=user_id
                ).execute()

        except HttpError as error:
            # Pass along the error
            raise error

        else:
            labels = [Label(name=x['name'], id=x['id']) for x in res['labels']]
            return labels


    def _get_messages_from_refs(
        self,
        user_id: str,
        message_refs: List[dict],
        attachments: Union['ignore', 'reference', 'download'] = 'reference',
        parallel: bool = True
    ) -> List[Message]:
        
        if not message_refs:
            return []

        if not parallel:
            return [self._build_message_from_ref(user_id, ref, attachments)
                    for ref in message_refs]
             
        max_num_threads = 12  # empirically chosen, prevents throttling
        target_msgs_per_thread = 10  # empirically chosen
        num_threads = min(
            math.ceil(len(message_refs) / target_msgs_per_thread),
            max_num_threads
        )
        batch_size = math.ceil(len(message_refs) / num_threads)
        message_lists = [None] * num_threads
        
        def thread_download_batch(thread_num):
            gmail = Gmail(creds=self.creds)
            start = thread_num * batch_size
            end = min(len(message_refs), (thread_num + 1) * batch_size)
            message_lists[thread_num] = [
                gmail._build_message_from_ref(
                    user_id, message_refs[i], attachments
                )
                for i in range(start, end)
            ]
          
        threads = [
            threading.Thread(target=thread_download_batch, args=(i,))
            for i in range(num_threads)
        ]
        
        for t in threads:
            t.start()

        for t in threads:
            t.join()
        return sum(message_lists, [])

    def _build_message_from_ref(
        self,
        user_id: str,
        message_ref: dict,
        attachments: Union['ignore', 'reference', 'download'] = 'reference',
    ) -> Message or HttpError:

        try:
            # Get message JSON
            with build(self.API_SERVICE, self.API_VERSION, credentials=self.credentials) as service:
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
            snippet = html.unescape(message['snippet'])


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
                    with build(self.API_SERVICE, self.API_VERSION, credentials=self.credentials) as service:
                        attm = Attachment(service, user_id, msg_id,
                                          part['attachment_id'], part['filename'],
                                          part['filetype'], part['data'])
                    attms.append(attm)
           
            with build(self.API_SERVICE, self.API_VERSION, credentials=self.credentials) as service:
                return Message(service, user_id, msg_id, thread_id, recipient, 
                    sender, subject, date, snippet, plain_msg, html_msg, label_ids,
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


    def _create_message(
        self,
        sender: str,
        to: str, 
        subject: str = '',
        msg_html: str = None,
        msg_plain: str = None,
        cc: List[str] = None,
        bcc: List[str] = None,
        attachments: List[str] = None,
        signature: bool = False
    ) -> dict:

        msg = MIMEMultipart('mixed' if attachments else 'alternative')
        msg['To'] = to
        msg['From'] = sender
        msg['Subject'] = subject

        if cc:
            msg['Cc'] = ', '.join(cc)

        if bcc:
            msg['Bcc'] = ', '.join(bcc)

        if signature:
            account_sig = self._get_alias_info(sender, 'me')['signature']
            if msg_html is None:
                msg_html = ''

            msg_html += "<br /><br />" + account_sig

        attach_plain = MIMEMultipart('alternative') if attachments else msg
        attach_html = MIMEMultipart('related') if attachments else msg

        if msg_plain:
            attach_plain.attach(MIMEText(msg_plain, 'plain'))

        if msg_html:
            attach_html.attach(MIMEText(msg_html, 'html'))

        if attachments:
            attach_plain.attach(attach_html)
            msg.attach(attach_plain)

            self._ready_message_with_attachments(msg, attachments)

        return {
            'raw': base64.urlsafe_b64encode(msg.as_string().encode()).decode()
        }


    def _get_alias_info(
        self,
        send_as_email: str,
        user_id: str = 'me'
    ) -> dict:
        
        res = None
        with build(self.API_SERVICE, self.API_VERSION, credentials=self.credentials) as service:
            res =  self.service.users().settings().sendAs().get(
                       sendAsEmail=send_as_email, userId=user_id).execute
        
        return res