import time
from datetime import datetime
import pytz
from extensions import db, Message, mail
from dotenv import load_dotenv
from time import sleep
from urllib.parse import quote
import os
from flask import flash
from pathlib import Path

load_dotenv()


def send_email_school(subject, recipients, body, html, image_dict):
    message = Message(subject, sender=("Writart School", 'writartstudios@gmail.com'), recipients=recipients)
    message.body = body
    if html:
        message.html = html
        root_path = 'static/images'
        if image_dict:
            for n in range(len(image_dict['file'])):
                file_format = 'image/' + image_dict['file'][n].split('.')[-1]
                message.attach(image_dict['file'][n], file_format,
                               open(os.path.join(root_path, image_dict['path'][n], image_dict['file'][n]), 'rb').read(),
                               'inline')
                # headers=[['content-ID', '<' + image_dict['file'][n].split('.')[0] + '>'], ])
    mail.send(message)
    print("Mail sent")


def send_email_studio(subject, recipients, body, html, image_dict):
    message = Message(subject, sender=("Writart Studio", 'writartstudios@gmail.com'), recipients=recipients)
    message.body = body
    if html:
        message.html = html
        root_path = '../static/images'
        if image_dict:
            for n in range(len(image_dict['file'])):
                file_format = 'image/' + image_dict['file'][n].split('.')[-1]
                message.attach(image_dict['file'][n], file_format,
                               open(os.path.join(root_path, image_dict['path'][n], image_dict['file'][n]), 'rb').read(),
                               'inline')
                # headers=[['content-ID', '<' + image_dict['file'][n].split('.')[0] + '>'], ])
    mail.send(message)
    print("Mail sent")


def send_email_support(subject, recipients, body, html, image_dict):
    message = Message(subject, sender=("Writart Support", "writartstudios@gmail.com"), recipients=recipients)
    message.body = body
    if html:
        message.html = html
        root_path = 'static/images'
        if image_dict:
            for n in range(len(image_dict['file'])):
                file_format = 'image/' + image_dict['file'][n].split('.')[-1]
                message.attach(image_dict['file'][n], file_format, open(os.path.join(root_path, image_dict['path'][n],
                                                                                     image_dict['file'][n]),
                                                                        'rb').read(), 'inline',)
                               # headers=[['content-ID', '<' + image_dict['file'][n].split('.')[0] + '>'], ])
    mail.send(message)
    print("Mail sent")


def send_email_with_reply(subject, sender_mail, recipients_list, message_body):
    message = Message(subject, sender=("Writart Studio", "writartstudios@gmail.com"), recipients=recipients_list, reply_to=sender_mail)
    message.body = message_body
    mail.send(message)
    print("mail sent")


def send_email_with_pdf_attachment(subject, reply_back_email, recipients_list, message_body, attachment_file_path):
    message = Message(subject, sender=("Writart Studio", "writartstudios@gmail.com"), recipients=recipients_list, reply_to=reply_back_email)
    message.body = message_body
    with open(attachment_file_path, 'rb') as fp:
        message.attach(
            filename=Path(attachment_file_path).name,
            content_type="application/pdf", 
            data=fp.read()
        )
    mail.send(message)
    print("mail sent")