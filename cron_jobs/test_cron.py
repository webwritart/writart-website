import operations.messenger as m
import datetime
from flask import current_app

time_stamp = datetime.datetime.now()


def send_mail():
    m.send_email_school('cron test 131', ['shwetabhartist@gmail.com'], 'test for cron', '', '')
    print(f"{time_stamp}- mail sent!")

