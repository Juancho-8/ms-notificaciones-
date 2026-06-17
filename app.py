from flask import Flask, request, jsonify
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
import os, pickle, base64
from email.mime.text import MIMEText
from twilio.rest import Client as TwilioClient
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

SCOPES = ['https://www.googleapis.com/auth/gmail.send']

TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID', '')
TWILIO_AUTH_TOKEN  = os.environ.get('TWILIO_AUTH_TOKEN', '')
TWILIO_WHATSAPP_FROM = os.environ.get('TWILIO_WHATSAPP_FROM', 'whatsapp:+14155238886')

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


@app.route("/send-whatsapp", methods=["POST"])
def send_whatsapp():
    data = request.json
    to = data["to"]
    message_text = data["message"]

    if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN:
        return jsonify({"error": "Credenciales Twilio no configuradas"}), 500

    client = TwilioClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    to_whatsapp = f"whatsapp:{to}" if not to.startswith("whatsapp:") else to
    msg = client.messages.create(
        body=message_text,
        from_=TWILIO_WHATSAPP_FROM,
        to=to_whatsapp,
    )
    return jsonify({"message": "WhatsApp enviado", "sid": msg.sid})


if __name__ == "__main__":
    app.run(port=5000)