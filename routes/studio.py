from flask import Blueprint, render_template, request, redirect, url_for, session, flash, send_file
import os
from flask_login import current_user
from werkzeug.utils import secure_filename
from extensions import db
from models.member import Member
from operations.miscellaneous import allowed_file
from operations.artist_tools import add_watermark, delete_single_watermarked_image


studio = Blueprint('studio', __name__, static_folder="static", template_folder='templates/studio/')


@studio.route('/', methods=['GET', 'POST'])
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
        return redirect(url_for('studio.portfolio', member=member.name.split()[0]))
    return render_template('studio.html', members=members)


@studio.route('/portfolio/<member>')
def portfolio(member):
    artist_dict = session['dict']
    return render_template('portfolio.html', dict=artist_dict)


@studio.route('/artist_tools', methods=['GET', 'POST'])
def artist_tools():
    folder_path = f"static/files/users/{current_user.name.split()[0]}{str(current_user.id)}/watermark_output"
    photo_path_list = []
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    photo_list = os.listdir(folder_path)
    for photo in photo_list:
        path = f"../{folder_path}/{photo}"
        photo_path_list.append(path)
    folder_name = current_user.name.split()[0] + str(current_user.id)

    if request.form.get('submit') and request.form.get('submit') == 'upload_photos':
        allowed_extensions = {'png', 'jpg'}

        if 'file' not in request.files:
            flash('No file part', 'error')
            return redirect(request.url)
        files = request.files.getlist('file')

        folder = f"static/files/users/{folder_name}/watermark_input"
        output_folder = f"static/files/users/{folder_name}/watermark_output"
        if not os.path.exists(folder):
            os.mkdir(folder)
        if not os.path.exists(output_folder):
            os.mkdir(output_folder)

        for file in files:
            if file.filename == '':
                flash('No selected file', 'error')
                return redirect(request.url)
            if file and allowed_file(file.filename, allowed_extensions):
                filename = secure_filename(file.filename)
                file.save(f"{folder}/{filename}")
                input_path = f"{folder}/{filename}"
                watermark_text = request.form.get('watermark-text')
                output_path = f"{output_folder}/{filename}"
                color = request.form.get('color')

                add_watermark(input_path, watermark_text, output_path, color)

                return redirect(url_for('studio.artist_tools'))
    if request.form.get('download'):
        image = request.form.get('download')
        file_path = f"static/files/users/{current_user.name.split()[0]}{str(current_user.id)}/watermark_output/{image}"
        return send_file(path_or_file=file_path, as_attachment=True)
    if request.form.get('delete'):
        image = request.form.get('delete')
        file_path = f"static/files/users/{current_user.name.split()[0]}{str(current_user.id)}/watermark_output/{image}"
        delete_single_watermarked_image(file_path)
        flash("Successfully deleted!", "success")
        return redirect(url_for('studio.artist_tools'))
    total_watermarked_photos = len(photo_path_list)

    return render_template('artist_tools.html', folder_name=folder_name, photo_list=photo_list,
                           logged_in=current_user.is_authenticated, total_watermarked=total_watermarked_photos)
