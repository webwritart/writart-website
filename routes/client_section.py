from flask import Blueprint, render_template, request, redirect, url_for, session, flash, send_file
from extensions import db
from flask_login import current_user, login_required
from models.member import Role

client_section = Blueprint('client_section', __name__, static_folder="static",
                           template_folder='templates/client_section/')


@login_required
@client_section.route('/', methods=['GET', 'POST'])
def client_dashboard():
    client = db.session.query(Role).filter_by(name='client').one_or_none()
    return render_template('client_dashboard.html', logged_in=current_user.is_authenticated, client=client)
