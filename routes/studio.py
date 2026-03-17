import pprint
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, send_file
import os
from flask_login import current_user
from werkzeug.utils import secure_filename
from extensions import db, current_year, list_files_in_directory, list_folders_in_directory
from models.member import Member
from operations.miscellaneous import allowed_file, text_match
from operations.artist_tools import add_watermark, delete_single_watermarked_image, delete_all_from_user
from models.artist_data import ArtistData
from models.artwork import Portrait
from pathlib import Path, PureWindowsPath

studio = Blueprint('studio', __name__, static_folder="static", template_folder='templates/studio/')


@studio.route('/', methods=['GET', 'POST'])
def home():
    members = []
    result = db.session.query(Member).all()
    for member in result:
        members.append(member)
        # print(member.sex)

    if request.method == 'POST':

        member_uuid = request.form.get('uuid')
        member = db.session.query(Member).filter_by(uuid=member_uuid).one()

        return redirect(url_for('studio.portfolio', member_uuid=member_uuid))
    return render_template('studio.html', members=members)


@studio.route('/portfolio/<member_uuid>')
def portfolio(member_uuid):
    member_uuid = member_uuid
    member = db.session.query(Member).filter_by(uuid=member_uuid).one_or_none()
    member_id = member.id
    first_name = member.name.split(' ')[0]
    artist_dict = {}
    artworks_thumbnail_dir = f'static/files/users/{member_id}/artworks/thumbnail/'
    artworks_large_dir = f'static/files/users/{member_id}/artworks/large/'
    index = 1
    for entry in os.scandir(artworks_thumbnail_dir):
        if entry.is_file():
            thumbnail_path = f'/{artworks_thumbnail_dir}{entry.name}'
            large_path = f'/{artworks_large_dir}{entry.name}'
            title = os.path.splitext(os.path.basename(entry.name))[0]
            img = {
                'title': title,
                'thumbnail': thumbnail_path,
                'large': large_path
            }
            artist_dict[index] = img
            index += 1
    return render_template('portfolio.html', dict=artist_dict)


@studio.route('/artist_tools', methods=['GET', 'POST'])
def artist_tools():
    total_file_size = 0
    total_final_file_size = 0
    file_no = 0
    folder_path = f"static/files/users/{current_user.name.split()[0]}{str(current_user.id)}/watermark_output"
    photo_path_list = []
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    photo_list = os.listdir(folder_path)
    for photo in photo_list:
        path = f"../{folder_path}/{photo}"
        photo_path_list.append(path)
    folder_name = current_user.name.split()[0] + str(current_user.id)
    watermark_text = request.form.get('watermark-text')
    folder = f"static/files/users/{folder_name}/watermark_input"
    output_folder = f"static/files/users/{folder_name}/watermark_output"
    if not os.path.exists(folder):
        os.mkdir(folder)
    if not os.path.exists(output_folder):
        os.mkdir(output_folder)

    if request.method == 'POST':
        if request.form.get('submit') and request.form.get('submit') == 'upload_photos':
            allowed_extensions = {'png', 'jpg', 'jpeg'}
            intensity = request.form.get('intensity')
            size = request.form.get('size')

            if 'file' not in request.files:
                flash('No file part', 'error')
                return redirect(request.url)
            files = request.files.getlist('file')

            for file in files:
                if file.filename == '':
                    flash('No selected file', 'error')
                    return redirect(request.url)
                if file and allowed_file(file.filename, allowed_extensions):
                    filename = secure_filename(file.filename)
                    file.save(f"{folder}/{filename}")
                    file_size = os.path.getsize(f"{folder}/{filename}")
                    total_file_size += file_size
                else:
                    flash("some problem occured!", "error")

            if total_file_size > 104857600:
                flash("Total file size exceeds 100 MB. Please upload less files at one time", "error")
            else:
                for f in files:
                    if f.filename != '' and f and allowed_file(f.filename, allowed_extensions):
                        filename = secure_filename(f.filename)
                        input_path = f"{folder}/{filename}"
                        output_path = f"{output_folder}/{filename}"
                        color = request.form.get('color')

                        file_final_size = add_watermark(input_path, watermark_text, output_path, color, intensity, size)
                        total_final_file_size += file_final_size
                        file_no += 1
                    else:
                        flash("Some error occured!", "error")
            watermarked_artworks = current_user.artist_data.watermarked_artworks
            current_user.artist_data.watermarked_artworks = watermarked_artworks + file_no

            memory_occupied_total = current_user.artist_data.memory_occupied_total
            current_user.artist_data.memory_occupied_total = memory_occupied_total + total_final_file_size
            db.session.commit()

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
        if request.form.get('delete_all'):
            folder = f"{current_user.name.split()[0]}{str(current_user.id)}"
            delete_all_from_user(folder)
            flash("All files successfully deleted!", "success")
            return redirect(url_for('studio.artist_tools'))
    total_watermarked_photos = len(photo_path_list)

    return render_template('artist_tools.html', folder_name=folder_name, photo_list=photo_list,
                           logged_in=current_user.is_authenticated, total_watermarked=total_watermarked_photos)

@studio.route('/portraits', methods=['GET', 'POST'])
def portraits():
    artwork_dict = {}

    base_path = 'static/files/users/477706/artworks/portrait/thumbnail'
    for file in list_files_in_directory(base_path):
        title_raw = PureWindowsPath(file).name
        path = file
        uuid = title_raw.split('.')[0].split('-')[1].split('_')[0]
        artist = db.session.query(Portrait).filter_by(uuid=uuid).scalar().artist
        title = title_raw.split('.')[0].split('-')[0].replace('_', ' ')
        artwork_dict[uuid] = {'title': title, 'path': path, 'artist': artist}


    return render_template('portraits.html', artwork_dict=artwork_dict)


@studio.route('/portrait-detail', methods=['GET', 'POST'])
def portrait_detail():
    uuid = request.args.get('uuid')
    title = request.args.get('title')
    img_path = ''
    base_path = 'static/files/users/477706/artworks/portrait/large'
    search = True
    while search:
        for file in list_files_in_directory(base_path):
            path = str(PureWindowsPath(file))
            if uuid in path:
                img_path = path
                search = False
    portrait = db.session.query(Portrait).filter_by(uuid=uuid).scalar()
    description = portrait.description
    medium = portrait.medium
    artist = portrait.artist
    return render_template('portrait-detail.html', img_path=img_path, title=title, description=description,
                           medium=medium, artist=artist)


@studio.route('/paintings', methods=['GET', 'POST'])
def paintings():
    return render_template('paintings.html')


