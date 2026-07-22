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
                all_artworks = db.session.query(Artwork).all()
                for a in all_artworks:
                    existing_uuid_list.append(a.uuid)

                uuid = create_uuid(existing_uuid_list=existing_uuid_list, uuid_length_in_digit=8)
                # ----------------------------------- Save artwork file -----------------------------------
                artwork_save_path = f"/static/files/users/{current_user.uuid}/artworks/spiritual/large/"
                artwork_thumbnail_save_path = f"/static/files/users/{current_user.uuid}/artworks/spiritual/thumbnail/"
                
                file.save(os.path.join(artwork_save_path, filename))
                # ----------------------------------- Add to database -------------------------------------
                if file.filename != '':
                    entry = Artwork(
                        uuid=uuid,
                        title=title,
                        category=category,
                        theme='spiritual',
                        member_id=current_user.id
                    )
                    db.session.add(entry)
                    db.session.commit()
                return jsonify({"success": True, "message": "Successfully added artwork"})
    
    return '', 204
