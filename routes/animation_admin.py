from flask import Blueprint, render_template, request, redirect, url_for, session, flash, send_file
from extensions import db, current_year
from operations.miscellaneous import allowed_file
from flask_login import login_required, current_user
from models.member import Member, Role, Project

animation_admin = Blueprint('animation_admin', __name__, static_folder="static",
                            template_folder='templates/animation_admin/')

clients = {}
projects = {}


@login_required
@animation_admin.route('/', methods=['GET', 'POST'])
def home():
    if db.session.query(Role).filter(Role.name == 'animation_admin').scalar() in current_user.role:
        destination = request.args.get('destination')
        if destination == 'add_new_project':
            return render_template('add_new_project.html', logged_in=current_user.is_authenticated)
        if destination == 'assign_project':

            projects_data = db.session.query(Project).all()
            for project in projects_data:
                project_name = project.name.replace(" ", "_")
                project_id = project.id
                projects[project_name] = project_id
            client_role = db.session.query(Role).filter_by(name='client').one_or_none()
            for member in db.session.query(Member):
                if client_role in member.role:
                    name = member.name.replace(" ", "_")
                    email = member.email
                    clients[name] = email
            # for client in clients:
                # print(f'Client: {client}')
                # print(clients[client])
                # print(f'Client: {client[0]}')
            return render_template('assign_project_clients.html', logged_in=current_user.is_authenticated,
                                   projects=projects, clients=clients)
        if request.method == 'POST' and request.form.get('submit') == 'create_new_project':
            project_name = request.form.get('name')
            project_short_des = request.form.get('short-description')
            project_detailed_des = request.form.get('detailed-description')
            producers = request.form.get('producers')
            sponsors = request.form.get('sponsors')
            start_date = request.form.get('start_date')
            deadline = request.form.get('deadline')
            category = request.form.get('category')

            entry = Project(
                name=project_name,
                category=category,
                short_description=project_short_des,
                detailed_description=project_detailed_des,
                start_date=str(start_date),
                deadline=str(deadline),
                sponsors=sponsors,
                producers=producers
            )
            db.session.add(entry)
            db.session.commit()
            flash('New Project successfully created!', 'success')
            return redirect(url_for('animation_admin.home', destination='add_new_project'))

        if request.method == 'POST' and request.form.get('submit') == 'assign_project':
            cl = request.form.get('client')
            client_email = clients[cl]
            pr = request.form.get('project')
            project_id = projects[pr]
            client = db.session.query(Member).filter_by(email=client_email).scalar()
            project = db.session.query(Project).filter_by(id=project_id).scalar()

            if project not in client.project:
                client.project.append(project)
                db.session.commit()
                flash('Project assigned successfully!', 'success')
            else:
                flash('Project already assigned', 'error')
            return redirect(url_for('animation_admin.home', destination='assign_project'))

        if request.method == 'POST' and request.form.get('submit') == 'revoke_project':
            cl = request.form.get('client1')
            client_email = clients[cl]
            pr = request.form.get('project1')
            project_id = projects[pr]
            client = db.session.query(Member).filter_by(email=client_email).scalar()
            project = db.session.query(Project).filter_by(id=project_id).scalar()

            if project in client.project:
                client.project.remove(project)
                db.session.commit()
            flash('Access revoked successfully!', 'success')
            return redirect(url_for('animation_admin.home', destination='assign_project'))

        return render_template('animation_admin_home.html', logged_in=current_user.is_authenticated, current_year=current_year)
    else:
        return render_template('admin_area.html')
