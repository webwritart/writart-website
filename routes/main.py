import os

from flask import Blueprint, render_template
from extensions import login_manager, db
from models.tool import Tools
from models.member import Member, Workshop, Role
from flask_login import current_user


main = Blueprint('main', __name__, static_folder='static', template_folder='templates')


@main.route('/')
def home():
    admin = db.session.query(Role).filter_by(name='admin').one_or_none()
    return render_template('index.html', logged_in=current_user.is_authenticated, admin=admin)
