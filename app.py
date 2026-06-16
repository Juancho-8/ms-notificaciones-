from flask import Flask, request, jsonify
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
import os, pickle, base64
from email.mime.text import MIMEText

app = Flask(__name__)

SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def authenticate_gmail():
    creds = None
    if os.path.exists('confidencial/token.pickle'):
        with open('confidencial/token.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception:
                creds = None

        if not creds or not creds.valid:
            flow = InstalledAppFlow.from_client_secrets_file(
                'confidencial/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        with open('confidencial/token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return creds


def create_message(sender, to, subject, message_text):
    message = MIMEText(message_text)
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    raw = base64.urlsafe_b64encode(message.as_bytes())
    return {'raw': raw.decode()}


@app.route("/send-email", methods=["POST"])
def send_email():
    data = request.json

    to = data["to"]
    subject = data["subject"]
    message_text = data["message"]

    creds = authenticate_gmail()
    service = build('gmail', 'v1', credentials=creds)

    message = create_message("juanmagudelolopez@gmail.com", to, subject, message_text)

    service.users().messages().send(userId="me", body=message).execute()

    return jsonify({"message": "Correo enviado correctamente"})


if __name__ == "__main__":
    app.run(port=5000)