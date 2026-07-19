from flask_login import current_user
from flask import Blueprint, request, render_template, redirect, flash, send_file
from operations.miscellaneous import *
from models.member import Role, Project
from extensions import db, p
import os

tools = Blueprint('tools', __name__, static_folder="static", template_folder='templates/client_section/')


@tools.route('/assigned_client_verified', methods=['GET', 'POST'])
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
    
@tools.route('/image_to_pdf', methods=['GET', 'POST'])
def image_to_pdf():
    if request.method == 'POST':
        if request.form.get('submit') == "images_to_pdf":
            file_name = request.form.get('file_name')
            files = request.files.getlist('files')
            output_pdf_directory = f"./static/files/users/{current_user.uuid}/temp/pdf/"

            if not os.path.exists(output_pdf_directory):
                p('not exits path')
                os.makedirs(output_pdf_directory)

            delete_all_files_in_directory(output_pdf_directory)
            pdf_file_path = multiple_images_to_pdf(files, '', output_pdf_directory, file_name, 50)
            return send_file(pdf_file_path, as_attachment=True)
    return '', 204 
