from flask_login import current_user
from flask import Blueprint
from models.member import Role, Project
from extensions import db

tools = Blueprint('tools', __name__, static_folder="static", template_folder='templates/client_section/')


def assigned_client_verified(project_id):
    project = db.session.query(Project).filter_by(id=project_id).scalar()
    client = db.session.query(Role).filter_by(name='client').one_or_none()
    if current_user.is_authenticated and client in current_user.role:
        if project in current_user.project:
            return True
        else:
            return False
    else:
        return False
