from flask import Blueprint, render_template
from extensions import login_manager, db
from models.member import Member, Workshop, Role
from flask_login import current_user
from operations.miscellaneous import log
from models.artist_data import ArtistData
from operations.artist_tools import delete_watermarked_images


main = Blueprint('main', __name__, static_folder='static', template_folder='templates')


@main.route('/')
def home():
    upcoming_workshop_list = []

    admin = db.session.query(Role).filter_by(name='admin').one_or_none()
    client = db.session.query(Role).filter_by(name='client').one_or_none()
    animation_admin = db.session.query(Role).filter_by(name='animation_admin').one_or_none()

    workshops = db.session.query(Workshop)
    for workshop in workshops:
        if not workshop.reg_start:
            upcoming_workshop_list.append(workshop.name)

    return render_template('index.html', logged_in=current_user.is_authenticated, admin=admin, client=client,
                           animation_admin=animation_admin, upcoming_workshop_list=upcoming_workshop_list)


@main.route('/privacy_policy')
def privacy_policy():
    return render_template('privacy_policy.html')

