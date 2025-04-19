from flask import Blueprint, render_template
from extensions import login_manager, db, current_year
from models.member import Member, Workshop, Role
from models.tool import Tools
from flask_login import current_user
from operations.miscellaneous import log
from models.artist_data import ArtistData
from operations.artist_tools import delete_watermarked_images

main = Blueprint('main', __name__, static_folder='static', template_folder='templates')


@main.route('/')
def home():
    upcoming_workshop_list = []
    current_ws = db.session.query(Tools).filter_by(keyword='current_workshop').one().data
    admin = db.session.query(Role).filter_by(name='admin').one_or_none()
    client = db.session.query(Role).filter_by(name='client').one_or_none()
    animation_admin = db.session.query(Role).filter_by(name='animation_admin').one_or_none()
    current_ws_category = db.session.query(Workshop).filter_by(name=current_ws).one().details.category
    current_ws_brief = db.session.query(Workshop).filter_by(name=current_ws).one().details.brief
    current_workshop = db.session.query(Workshop).filter_by(name=current_ws).one()
    current_ws_topic = current_workshop.topic
    current_ws_date = current_workshop.date
    current_ws_time = current_workshop.time

    workshops = db.session.query(Workshop).all()
    for workshop in workshops:
        if not workshop.reg_start:
            upcoming_workshop_list.append(workshop.name)

    return render_template('index.html', logged_in=current_user.is_authenticated, admin=admin, client=client,
                           animation_admin=animation_admin, upcoming_workshop_list=upcoming_workshop_list,
                           current_ws=current_ws, current_ws_category=current_ws_category,
                           current_ws_topic=current_ws_topic, current_ws_brief=current_ws_brief,
                           current_ws_date=current_ws_date, current_ws_time=current_ws_time, current_year=current_year)


@main.route('/privacy_policy')
def privacy_policy():
    return render_template('privacy_policy.html', current_year=current_year)

