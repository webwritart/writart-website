import datetime
import os
from werkzeug.security import generate_password_hash
from flask import Blueprint, render_template
from extensions import login_manager, db
from models.tool import Tools
from models.member import Member, Workshop, Role
from flask_login import current_user
import pandas as pd
from operations.messenger import send_email_school


main = Blueprint('main', __name__, static_folder='static', template_folder='templates')


@main.route('/')
def home():
    time_now = str(datetime.datetime.now()).split()[1]
    time = time_now.split('.')[0]
    scheduled_time = "17:07:00"

    if time == scheduled_time:
        send_email_school('scheduled_operation_test', ['shwetabhartist@gmail.com'], 'scheduled operation test', '', '')

    admin = db.session.query(Role).filter_by(name='admin').one_or_none()
    return render_template('index.html', logged_in=current_user.is_authenticated, admin=admin)


@main.route('/privacy_policy')
def privacy_policy():
    return render_template('privacy_policy.html')

