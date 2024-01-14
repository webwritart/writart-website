import os

from flask import Blueprint, render_template
from extensions import login_manager, db
from models.tool import Tools
from models.user import User, Workshop,Role
from flask_login import current_user


main = Blueprint('main', __name__, static_folder='static', template_folder='templates')


@main.route('/')
def home():
    # entry = User(
    #     email='shwetabhartist@gmail.com',
    #     password='12345',
    #     name='Shwetabh Suman',
    #     phone='8920351265',
    #     whatsapp='',
    #     profession='Artist',
    #     sex='male',
    #     dob='1994-03-01',
    #     state='Delhi',
    #     fb_url='',
    #     insta_url='',
    #     website='',
    #     registration_date=''
    # )

    # entry = Workshop(
    #     name='ws1',
    #     topic='test',
    #     date='2024-01-26',
    #     instructor='Shwetabh Suman',
    #     strength='',
    #     gross_revenue='',
    #     joining_link='',
    #     joining_link2='',
    #     joining_link3='',
    #     joining_link4='',
    #     yt_p1_id='',
    #     yt_p2_id='',
    #     yt_p3_id='',
    #     yt_p4_id='',
    #     reg_start='',
    #     reg_close=''
    # )

    # entry = Tools(
    #     keyword='last invoice',
    #     data=1
    # )
    # db.session.add(entry)
    # db.session.commit()
    return render_template('index.html', logged_in=current_user.is_authenticated)
