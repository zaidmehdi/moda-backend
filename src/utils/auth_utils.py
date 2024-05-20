import re

from flask import url_for
from flask_mail import Mail, Message


def validate_email(email:str):
    """Validate email format."""

    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    
    return re.match(email_regex, email)


def send_verification_email(user):
    """For users who signup"""

    mail = Mail()

    token = user.verification_token
    verification_link = url_for("auth.verify_email", token=token, _external=True)
    msg = Message(subject="Email Verification",
                  sender="mehdizaid02@gmail.com",
                  recipients=[user.email],
                  body=f"Please click the link to verify your email: {verification_link}")
    mail.send(msg)