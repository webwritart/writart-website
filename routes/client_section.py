from flask import Blueprint, render_template, request, redirect, url_for, session, flash, send_file
from extensions import db
from flask_login import current_user, login_required
from models.member import Role, Project

client_section = Blueprint('client_section', __name__, static_folder="static",
                           template_folder='templates/client_section/')


@login_required
@client_section.route('/', methods=['GET', 'POST'])
def client_dashboard():
    client = db.session.query(Role).filter_by(name='client').one_or_none()
    if client in current_user.role:
        client_project_list = current_user.project
        return render_template('client_dashboard.html', logged_in=current_user.is_authenticated, client=client,
                               client_project_list=client_project_list)


@login_required
@client_section.route('/project/', methods=['GET', 'POST'])
def project_page():
    project_id = request.args.get('project_id')
    project = db.session.query(Project).filter_by(id=project_id).scalar()
    client = db.session.query(Role).filter_by(name='client').one_or_none()
    if client in current_user.role and project in current_user.project:
        project_name = project.name
        project_producer = project.producers
        project_sponsors = project.sponsors
        project_category = project.category
        return render_template('project.html', project_name=project_name, project_producer=project_producer,
                               project_sponsors=project_sponsors, project_category=project_category)
    else:
        return render_template('admin_area.html')
