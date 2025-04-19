from flask import Blueprint, render_template, request, redirect, url_for, session, flash, send_file
from extensions import db, current_year
from flask_login import current_user, login_required
from models.member import Role, Project
from routes.tools import assigned_client_verified

client_section = Blueprint('client_section', __name__, static_folder="static",
                           template_folder='templates/client_section/')

project_id = ''


@client_section.route('/', methods=['GET', 'POST'])
def client_dashboard():
    if current_user.is_authenticated:
        client = db.session.query(Role).filter_by(name='client').one_or_none()
        if client in current_user.role:
            client_project_list = current_user.project
            return render_template('client_dashboard.html', logged_in=current_user.is_authenticated, client=client,
                                   client_project_list=client_project_list, current_year=current_year)
    else:
        return render_template('not_logged_in.html', current_year=current_year)


@client_section.route('/project/', methods=['GET', 'POST'])
def project_page():
    if current_user.is_authenticated:
        global project_id
        project_id = request.args.get('project_id')
        project = db.session.query(Project).filter_by(id=project_id).scalar()
        client = db.session.query(Role).filter_by(name='client').one_or_none()
        if client in current_user.role and project in current_user.project:
            project_name = project.name
            project_producer = project.producers
            project_sponsors = project.sponsors
            project_category = project.category
            return render_template('project.html', project_id=project_id, project_name=project_name,
                                   project_producer=project_producer,
                                   project_sponsors=project_sponsors, project_category=project_category,
                                   logged_in=current_user.is_authenticated, current_year=current_year)
    else:
        return render_template('not_logged_in.html', current_year=current_year)


@client_section.route('/animation_preproduction/', methods=['GET', 'POST'])
def animation_preproduction():
    if current_user.is_authenticated:
        global project_id
        project_id = request.args.get('project_id')
        if assigned_client_verified(project_id):
            return render_template('animation_preproduction.html',logged_in=current_user.is_authenticated, project_id=project_id,
                                   current_year=current_year)
    else:
        return render_template('not_logged_in.html', current_year=current_year)


@client_section.route('/animation_production/', methods=['GET', 'POST'])
def animation_production():
    if current_user.is_authenticated:
        global project_id
        project_id = request.args.get('project_id')
        if assigned_client_verified(project_id):
            return render_template('animation_production.html',logged_in=current_user.is_authenticated, project_id=project_id,
                                   current_year=current_year)
    else:
        return render_template('not_logged_in.html', current_year=current_year)


@client_section.route('/animation_postproduction/', methods=['GET', 'POST'])
def animation_postproduction():
    if current_user.is_authenticated:
        global project_id
        project_id = request.args.get('project_id')
        if assigned_client_verified(project_id):
            return render_template('animation_postproduction.html',logged_in=current_user.is_authenticated, project_id=project_id,
                                   current_year=current_year)
    else:
        return render_template('not_logged_in.html', current_year=current_year)
