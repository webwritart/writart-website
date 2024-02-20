from flask import Blueprint, render_template
from extensions import login_manager, db
from models.member import Member, Workshop, Role
from flask_login import current_user
from operations.miscellaneous import log
from models.artist_data import ArtistData


main = Blueprint('main', __name__, static_folder='static', template_folder='templates')


@main.route('/')
def home():
    member = db.session.query(Member).filter_by(id=47).one()
    entry = ArtistData(
        artist=member.name,
        watermarked_artworks=0,
        gallery_artworks=0,
        all_collections=0,
        commission_collections=0,
        sold_artworks=0,
        queried_artworks=0,
        shipped_artworks=0,
        contracted_artworks=0,
        sold_commissions=0,
        memory_occupied_total=0,
        memory_occupied_gallery=0,
        member=member
    )
    db.session.add(entry)
    db.session.commit()

    admin = db.session.query(Role).filter_by(name='admin').one_or_none()
    return render_template('index.html', logged_in=current_user.is_authenticated, admin=admin)


@main.route('/privacy_policy')
def privacy_policy():
    return render_template('privacy_policy.html')

