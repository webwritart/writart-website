import time
from datetime import datetime
import pytz
from extensions import db, Message, mail
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from time import sleep
from urllib.parse import quote
import os
from flask import flash

load_dotenv()


def send_email_school(subject, recipients, body, html, image_dict):
    message = Message(subject, sender=("Writart Gurukul", 'writartstudios@gmail.com'), recipients=recipients)
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



