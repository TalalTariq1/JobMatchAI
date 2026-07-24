import base64
import json
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

from firebase_client import db

# "send only" permission, same as before — this doesn't change.
SCOPES = ["https://www.googleapis.com/auth/gmail.send"]


def save_gmail_token(user_id, credentials):
    """
    Saves this specific user's Gmail permission token into their own
    Firestore document, so we can reuse it later without asking them to
    click 'Allow' again every single time.
    """
    token_dict = json.loads(credentials.to_json())
    db.collection("users").document(user_id).set(
        {"gmailToken": token_dict}, merge=True
    )


def load_gmail_token(user_id):
    """
    Loads this specific user's saved Gmail token from Firestore, if one
    exists. Returns None if they've never connected Gmail yet.
    """
    doc = db.collection("users").document(user_id).get()
    if not doc.exists:
        return None
    data = doc.to_dict()
    token_dict = data.get("gmailToken")
    if not token_dict:
        return None
    return Credentials.from_authorized_user_info(token_dict, SCOPES)


def get_gmail_service(user_id):
    """
    Returns a ready-to-use Gmail API connection for this specific user,
    using their own saved token from Firestore. If their token has expired
    but can be automatically refreshed, this also handles that and re-saves
    the refreshed token.
    """
    creds = load_gmail_token(user_id)

    if not creds:
        raise Exception(
            f"No Gmail token found for user {user_id}. "
            "They need to connect Gmail first via /connect-gmail."
        )

    # Access tokens naturally expire after a while (Google does this for
    # security). If ours has expired, but we still have a valid "refresh
    # token", we can silently get a new one without bothering the user.
    if not creds.valid and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        save_gmail_token(user_id, creds)  # save the freshly refreshed token

    service = build("gmail", "v1", credentials=creds)
    return service


def create_message_with_attachment(to, subject, body_text, attachment_path):
    """
    Builds a real email message (subject, body, and a file attached), and
    encodes it into the exact text format Gmail's API requires. We don't
    set a 'from' address here — Gmail automatically fills that in as
    whichever real account is authorized to send, based on the token used.
    """
    message = MIMEMultipart()
    message["to"] = to
    message["subject"] = subject

    message.attach(MIMEText(body_text))

    with open(attachment_path, "rb") as attachment_file:
        part = MIMEApplication(attachment_file.read())
    part["Content-Disposition"] = f'attachment; filename="{os.path.basename(attachment_path)}"'
    message.attach(part)

    raw_bytes = message.as_bytes()
    raw_base64 = base64.urlsafe_b64encode(raw_bytes).decode()

    return {"raw": raw_base64}


def send_email(user_id, to, subject, body_text, attachment_path):
    """
    Sends a real email as THIS SPECIFIC USER, using their own connected
    Gmail account, with a file attached.
    """
    service = get_gmail_service(user_id)
    message = create_message_with_attachment(to, subject, body_text, attachment_path)
    sent_message = service.users().messages().send(userId="me", body=message).execute()
    return sent_message