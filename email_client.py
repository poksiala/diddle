import os
import sys
import traceback
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import db

BASE_URL = os.environ["BASE_URL"]

def send_email(subject: str, body: str, recipient: str):
  pass

email_env_vars = [
  "EMAIL_HOST",
  "EMAIL_PORT",
  "EMAIL_HOST_USER",
  "EMAIL_HOST_PASSWORD",
  "EMAIL_USE_TLS",
  "EMAIL_MESSAGE_FROM",
]

email_enabled = any(var in os.environ for var in email_env_vars)
if email_enabled:
  for var in email_env_vars:
    if var not in os.environ:
      raise Exception(f"Some EMAIL_ variables are set but {var} is not set")

  email_host = os.environ["EMAIL_HOST"]
  email_port = int(os.environ["EMAIL_PORT"])
  email_host_user = os.environ["EMAIL_HOST_USER"]
  email_host_password = os.environ["EMAIL_HOST_PASSWORD"]
  email_use_tls = os.environ["EMAIL_USE_TLS"].lower() in ["true", "1", "yes"]
  email_message_from = os.environ["EMAIL_MESSAGE_FROM"]

  print(f"SMTP email client enabled using email host {email_host}")

  def _actual_send_email(subject: str, body: str, recipient: str):
    if not email_enabled:
      return
    
    print("debug: subject:", subject)
    print("debug: body:", body)
    print("debug: recipient:", recipient)
    print("debug: email_host:", email_host)
    print("debug: email_port:", email_port)
    print("debug: email_host_user:", email_host_user)
    print("debug: email_host_password:", email_host_password)
    print("debug: email_use_tls:", email_use_tls)
    print("debug: email_message_from:", email_message_from)

    msg = MIMEMultipart()
    msg['From'] = email_host_user
    msg['To'] = recipient
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    with smtplib.SMTP(email_host, email_port) as server:
      if email_use_tls:
        server.starttls()

      server.login(email_host_user, email_host_password)
      server.send_message(msg)

  send_email = _actual_send_email
else:
  print("SMTP email client not enabled")

def send_participation_email_if_enabled(poll_id: str, voter_name: str):
  if email_enabled:
    poll = db.get_poll(poll_id)
    if not poll or poll.author_email is None:
      return

    try:
      send_email(
        subject=f"{voter_name} participated in your poll \"{poll.title}\"",
        body=f"{voter_name} participated in your diddle \"{poll.title}\".\n\n"
             f"View the results at {BASE_URL}/poll/{poll.id}\n"
             f"Manage your diddle at {BASE_URL}/manage/{poll.manage_code}\n"
              "You will be notified by email when someone participates.",
        recipient=poll.author_email,
      )
    except Exception as e:
      traceback.print_exc(file=sys.stderr)
      print(f"Failed to send participation email to {poll.author_email}", file=sys.stderr)

def send_poll_created_email_if_enabled(poll_id: str):
  if email_enabled:
    poll = db.get_poll(poll_id)
    if not poll or poll.author_email is None:
      return

    try:
      send_email(
        subject=f"You created a new diddle \"{poll.title}\"",
        body=f"Manage your diddle at {BASE_URL}/manage/{poll.manage_code}\n"
              "You will be notified by email when someone participates.",
        recipient=poll.author_email,
      )
    except Exception as e:
      traceback.print_exc(file=sys.stderr)
      print(f"Failed to send poll created email to {poll.author_email}", file=sys.stderr)