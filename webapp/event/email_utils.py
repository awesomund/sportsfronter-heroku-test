#coding: utf8
from sportsfronter.settings import ROOT_URL, EMAIL_HOST, SERVER_EMAIL, EMAIL_PORT, EMAIL_USE_TLS, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import logging
import os
import smtplib

logger = logging.getLogger("sportsfronter.event.email_utils")

def _create_html_mail_message(person, event, url_hash, category):

    event_dir = os.path.dirname(__file__)
    template_path = os.path.join(event_dir, 'static/event/email_template_phase2.html')

    email_template = ""
    with open(template_path, 'r') as f:
        email_template = f.read()

    email_template = email_template.decode("utf-8")

    email_template = email_template.replace("{{{ROOT_URL}}}", ROOT_URL)
    email_template = email_template.replace("{{{INVITATION_URL}}}", "/#/rsvp/%s" % url_hash)
    email_template = email_template.replace("{{{DATE}}}", event.start_datetime.strftime('%d/%m/%Y'))
    email_template = email_template.replace("{{{TIME}}}", event.start_datetime.strftime('%H:%M'))
    email_template = email_template.replace("{{{LOCATION}}}", event.location)
    email_template = email_template.replace("{{{EVENT_NAME}}}", event.title)
    email_template = email_template.replace("{{{NAME}}}", person.first_name + " " + person.last_name)
    email_template = email_template.replace("{{{TEAM}}}", event.team.name)
    email_template = email_template.replace("{{{CATEGORY}}}", category)

    return email_template

def _get_recipients(player):
    recipients = []
    if player.person.email:
        recipients.append(player.person.email)
    guardians = player.guardians.all()
    for guardian in guardians:
        if guardian.email:
            recipients.append(guardian.email)
    return recipients

def _create_email_connection():
    connection = smtplib.SMTP()
    connection.connect(EMAIL_HOST,EMAIL_PORT)
    connection.ehlo()
    if EMAIL_USE_TLS:
        connection.starttls()
        connection.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)

    return connection

def _send_single_event_mail(email_connection, player, event, to_address, url_hash, subject, category):
    html_text = _create_html_mail_message(player.person, event, url_hash, category)

    from_address = SERVER_EMAIL

    msg = MIMEMultipart('alternative')
    msg_text = MIMEText(html_text, 'html', 'UTF-8')
    msg['Subject'] = "Sportsfronter - " + subject + ": " + event.title.encode('UTF-8')
    msg['From'] = from_address
    msg['To'] = to_address

    msg.attach(msg_text)

    email_connection.sendmail(from_address, to_address, msg.as_string())

def _send_event_mail(event_players, event, subject, category):
    email_connection = _create_email_connection()

    for event_player in event_players:
        player = event_player.player
        url_hash = event_player.url_hash

        for recipient_email in _get_recipients(player):
            _send_single_event_mail(email_connection, player, event, recipient_email, url_hash, subject, category)

        if not event_player.sent:
            event_player.sent = True

        if event_player.answer == 5:
            event_player.answer = 4
        
        event_player.save()

    email_connection.quit()


def send_reminder_mail(event_players, event):
    _send_event_mail(event_players, event, "Purring", "PURRING")


def send_invite_mail(event_players, event):
    _send_event_mail(event_players, event, "Invitasjon", "INVITASJON")


def send_update_mail(event_players, event):
    _send_event_mail(event_players, event, "Oppdatering", "OPPDATERING")


def send_event_group_invite_and_update_mail(new_event_players, existing_event_players):
    email_connection = _create_email_connection()

    #invites:
    for new_event_player in new_event_players:
        player = new_event_player.player
        url_hash = new_event_player.url_hash

        for recipient_email in _get_recipients(player):
            _send_single_event_mail(email_connection, player, new_event_player.event, recipient_email, url_hash, "Invitasjon", "INVITASJON")

        if not new_event_player.sent:
            new_event_player.sent = True
            
        if new_event_player.answer == 5:
            new_event_player.answer = 4
    
        new_event_player.save()

    #updates:
    for existing_event_player in existing_event_players:
        player = existing_event_player.player
        url_hash = existing_event_player.url_hash

        for recipient_email in _get_recipients(player):
            _send_single_event_mail(email_connection, player, existing_event_player.event, recipient_email, url_hash, "Oppdatering", "OPPDATERING")

        if not existing_event_player.sent:
            existing_event_player.sent = True
            
        if existing_event_player.answer == 5:
            existing_event_player.answer = 4
    
        existing_event_player.save()



def _create_username_change_message(person, old_username, new_username):
    event_dir = os.path.dirname(__file__)
    template_path = os.path.join(event_dir, 'static/event/update_username_email_template.html')

    email_template = ""
    with open(template_path, 'r') as f:
        email_template = f.read()

    email_template = email_template.decode("utf-8")

    email_template = email_template.replace("{{{FIRST_NAME}}}", person.first_name)
    email_template = email_template.replace("{{{OLD_USERNAME}}}", old_username)
    email_template = email_template.replace("{{{NEW_USERNAME}}}", new_username)

    return email_template


def send_username_update_mail(person, old_username, new_username):
    html_text = _create_username_change_message(person, old_username, new_username)

    email_connection = _create_email_connection()
    from_address = SERVER_EMAIL
    to_address = person.email

    msg = MIMEMultipart('alternative')
    msg_text = MIMEText(html_text, 'html', 'UTF-8')
    msg['Subject'] = "Sportsfronter - " + "Nytt Brukernavn"
    msg['From'] = from_address
    msg['To'] = person.email

    msg.attach(msg_text)

    email_connection.sendmail(from_address, to_address, msg.as_string())
    msg['To'] = person.email
    email_connection.sendmail(from_address, old_username, msg.as_string())



