import os
from flask import Blueprint, render_template, request, flash, send_file, redirect, url_for, session, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from operations.artist_tools import add_watermark
from extensions import db, image_dict, current_year, p
from operations.messenger import *
from models.workshop_details import WorkshopDetails
from models.member import *
from flask_login import current_user, login_required, login_user, logout_user
from datetime import date, datetime
import random
from operations.miscellaneous import *
from models.artist_data import *
from models.news import News
from models.tool import SupportTicket, Tools
from models.artwork import *
from models.transactions import *
from routes import main
import random
from io import BytesIO
from zipfile import ZipFile, ZIP_DEFLATED
import shutil
from pathlib import Path


artist_dashboard_operations = Blueprint('artist_dashboard_operations', __name__, static_folder='static', template_folder='templates/artist_dashboard_operations')


@artist_dashboard_operations.route('/upload_artwork', methods=['GET', 'POST'])
def upload_artwork():
    if request.method == 'POST':
        if request.form.get('form-name') == 'upload-artwork':
            
            # 1. Check if the file part is present in the request
            if 'artwork-file' not in request.files:
                return jsonify({'error': 'No file part in the request'}), 400
                
            file = request.files['artwork-file']
            # 2. Check if the user submitted an empty form without selecting a file
            if file.filename == '':
                return jsonify({'error': 'No file selected'}), 400
            
            if file:
                title = request.form.get('title')
                category = request.form.get('category')
                filename = secure_filename(file.filename)

                existing_uuid_list = []
                all_artworks = db.session.query(Artwork)
                for a in all_artworks:
                    existing_uuid_list.append(a.uuid)

                uuid = create_uuid(existing_uuid_list=existing_uuid_list, uuid_length_in_digit=8)
                date_time_uploaded = datetime.now().replace(microsecond=0)
                # ----------------------------------- Save artwork file -----------------------------------
                artwork_save_path = f"./static/files/users/{current_user.uuid}/artworks/spiritual/large/"
                artwork_thumbnail_save_path = f"./static/files/users/{current_user.uuid}/artworks/spiritual/thumbnail/"

                if not os.path.exists(artwork_save_path):
                    os.makedirs(artwork_save_path)
                if not os.path.exists(artwork_thumbnail_save_path):
                    os.makedirs(artwork_thumbnail_save_path)
                file.save(artwork_save_path+filename)
                # ----------------------------------- Add to database -------------------------------------
                if file.filename != '':
                    entry = Artwork(
                        uuid=uuid,
                        title=title,
                        category=category,
                        theme='spiritual',
                        member_id=current_user.id,
                        date_time_uploaded=date_time_uploaded,
                        main_photo_path=artwork_save_path+filename
                    )
                    db.session.add(entry)
                    db.session.commit()
                return jsonify({"success": True, "message": "Successfully added artwork"})
    
    return '', 204


@artist_dashboard_operations.route('/pending_artwork_details_edit', methods=['GET', 'POST'])
def pending_artwork_details_edit():
    if request.method == 'POST':
        data = request.get_json()
        uuid = data
        return jsonify({"redirect_url": url_for('artist_dashboard_operations.pending_artwork_details_edit', uuid=uuid)})
    artwork_details_dict = {}

    uuid = request.args.get('uuid')
    try:
        artwork = db.session.query(Artwork).filter_by(uuid=uuid).scalar()
        artwork_details_dict = {'title': artwork.title,
                                'theme': artwork.theme,
                                'category': artwork.category,
                                'main_photo_path': artwork.main_photo_path,
                                'date_time_uploaded': artwork.date_time_uploaded}
    except Exception as e:
        p(e)

    admin = db.session.query(Role).filter_by(name='admin').scalar()
    return render_template('pending_artwork_details_edit.html', logged_in=current_user.is_authenticated, current_year=current_year, admin=admin,
                        artwork_details_dict=artwork_details_dict)