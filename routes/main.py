import os
from werkzeug.security import generate_password_hash
from flask import Blueprint, render_template
from extensions import login_manager, db
from models.tool import Tools
from models.member import Member, Workshop, Role
from flask_login import current_user


main = Blueprint('main', __name__, static_folder='static', template_folder='templates')


@main.route('/')
def home():
    # password = generate_password_hash(
    #     '12345',
    #     method='pbkdf2:sha256',
    #     salt_length=8
    # )
    # entry = Member(
    #     email= 'mango@writart.com',
    #     password = password,
    #     name = 'Mango Ji',
    #     phone = '56413483620',
    # )
    # db.session.add(entry)
    # db.session.commit()
    admin = db.session.query(Role).filter_by(name='admin').one_or_none()
    return render_template('index.html', logged_in=current_user.is_authenticated, admin=admin)
