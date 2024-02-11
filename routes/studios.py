from flask import Blueprint, render_template, request, redirect, url_for, session
from flask_login import current_user
from extensions import db
from models.member import Member


studios = Blueprint('studios', __name__, static_folder="static", template_folder='templates/studios/')


@studios.route('/', methods=['GET', 'POST'])
def home():
    members = []
    result = db.session.query(Member)
    for member in result:
        members.append(member)
        # print(member.sex)

    if request.method == 'POST':
        artist_dict = {
            'name': '',
            'sex': '',
            'dob': '',
            'state': ''
        }
        member_id = request.form.get('portfolio-link')
        member = db.session.query(Member).filter_by(id=member_id).one()
        artist_dict['name'] = member.name
        artist_dict['sex'] = member.sex
        artist_dict['dob'] = member.dob
        artist_dict['state'] = member.state

        session['dict'] = artist_dict
        return redirect(url_for('studios.portfolio', member=member.name.split()[0]))
    return render_template('studios.html', members=members)


@studios.route('/portfolio/<member>')
def portfolio(member):
    artist_dict = session['dict']
    return render_template('portfolio.html', dict=artist_dict)
