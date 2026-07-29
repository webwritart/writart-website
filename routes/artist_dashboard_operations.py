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
import json


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
                filename = secure_filename(file.filename)

                existing_uuid_list = []
                all_artworks = db.session.query(Artwork)
                for a in all_artworks:
                    existing_uuid_list.append(a.uuid)

                uuid = create_uuid(existing_uuid_list=existing_uuid_list, uuid_length_in_digit=8)
                date_time_uploaded = datetime.now().replace(microsecond=0)
                # ----------------------------------- Save artwork file -----------------------------------
                artwork_save_path = f"./static/files/users/{current_user.uuid}/artworks/spiritual/{uuid}/original/"
                temp_thumbnail_path = f"./static/files/users/{current_user.uuid}/temp/temp_thumbnails/"
                artwork_thumbnail_save_path = f"./static/files/users/{current_user.uuid}/artworks/spiritual/{uuid}/thumbnail/"

                if not os.path.exists(artwork_save_path):
                    os.makedirs(artwork_save_path)
                if not os.path.exists(artwork_thumbnail_save_path):
                    os.makedirs(artwork_thumbnail_save_path)
                os.makedirs(temp_thumbnail_path, exist_ok=True)

                file.save(artwork_save_path+filename)

                original_file_path = artwork_save_path+filename

                file_path = create_thumbnail_single(original_file_path, temp_thumbnail_path, 900)[0]
                webp_thumbnail_filepath = single_png_jpg_to_webp(file_path, artwork_thumbnail_save_path, quality=100)[0][1:]
                print_size_list = calculate_print_size_list(original_file_path)
                json_print_size_list = json.dumps(print_size_list)

                os.remove(file_path)
                p('Saved artwork original and thumbnail')
                artwork_save_path = artwork_save_path[1:]+filename
                # ----------------------------------- Add to database -------------------------------------
                if file.filename != '':
                    entry = Artwork(
                        uuid=uuid,
                        title=title,
                        theme='spiritual',
                        member_id=current_user.id,
                        date_time_uploaded=date_time_uploaded,
                        main_photo_path=webp_thumbnail_filepath,
                        hd_photo_path=artwork_save_path,
                        print_size_list=json_print_size_list
                    )
                    db.session.add(entry)
                    db.session.commit()
                return jsonify({"success": True, "message": "Successfully added artwork"})
    
    return '', 204


@artist_dashboard_operations.route('/pending_artwork_details_edit', methods=['GET', 'POST'])
def pending_artwork_details_edit():
    admin = db.session.query(Role).filter_by(name='admin').scalar()
    step_1 = 'pending'
    step_2 = 'pending'
    photo_size_list = []
    canvas_size_list = []

    if current_user.is_authenticated:
        if request.method == 'POST' and request.is_json:
            data = request.get_json()
            uuid = data
            session['pending_artwork_uuid'] = uuid
            return jsonify({"redirect_url": url_for('artist_dashboard_operations.pending_artwork_details_edit')})
        # -------------------------------------------------------------------------------------------------------------
        form_name = ''
        artwork_details_dict = {}
        pending_details_artworks_uuid_list = []
        pending_details_artworks_dict = {}

        # --------------------------------------- PENDING ARTWORKS COLUMN ---------------------------------------------
        all_artworks = current_user.artworks
        for a in all_artworks:
            details = [a.theme, a.product_title, a.short_description, a.medium, a.original_price, a.original_available, a.creation_year, a.main_photo_path,
                        a.sale_status]
            if any(item is None for item in details):
                pending_details_artworks_uuid_list.append(a.uuid)
        for uuid in pending_details_artworks_uuid_list:
            a = db.session.query(Artwork).filter_by(uuid=uuid).scalar()
            artwork_title = a.title
            main_photo_path = a.main_photo_path
            uuid = a.uuid
            pending_details_artworks_dict[artwork_title] = {'main_photo_path': main_photo_path, 'uuid': uuid}
        pending_artwork_count = len(pending_details_artworks_dict)
        pending_details_artworks_dict = dict(reversed(pending_details_artworks_dict.items()))

        # -------------------------------------- PENDING ARTWORK EDITING SECTION -----------------------------------------------
        uuid = session.get('pending_artwork_uuid')
        artwork = db.session.query(Artwork).filter_by(uuid=uuid).scalar()
        if artwork.product_title:
            form_name = 'variants'
            step_1 = 'done'
        artwork_details_dict = {'uuid': uuid,
                                'title': artwork.title,
                                'theme': artwork.theme,
                                'main_photo_path': artwork.main_photo_path,
                                'date_time_uploaded': artwork.date_time_uploaded,
                                'print': artwork.print}
        
        # -------------------------------------- PRINT VARIANTS PRICES ----------------------------------------------
        if artwork.print == 'yes' or artwork.print == 'limited':
            all_print_sizes_dict = json.loads(artwork.print_size_list)
            a_size_list = all_print_sizes_dict['a']
            photo_size_list = all_print_sizes_dict['photo']
            canvas_size_list = all_print_sizes_dict['canvas']
        # ----------------------------------------- FORM POST --------------------------------------------------------
        if request.method == 'POST':
            if request.form.get('submit') == 'submit-artwork-details':
                product_title = request.form.get('product_title')
                short_description = request.form.get('short-description')
                long_description = request.form.get('long-description')
                year = request.form.get('creation-year')
                medium = request.form.get('medium')
                surface = request.form.get('surface')
                width = request.form.get('width')
                height = request.form.get('height')
                original_available = request.form.get('original-available')
                original_price = request.form.get('original-price')
                original_discount_percent = request.form.get('original-discount-percent')
                sell_prints = request.form.get('sell-prints')
                limited_print_count = request.form.get('limited-print-count')
                recreation = request.form.get('recreation')
                limited_recreation_count = request.form.get('limited-recreation-count')
                uuid = request.form.get('uuid')
                if width and height:
                    size_values = [int(width), int(height)]
                    smaller_value = ''
                    larger_value = ''
                    for i in size_values:
                        if i == int(min(size_values)):
                            smaller_value = i
                        else:
                            larger_value = i
                    original_size = f"{smaller_value} x {larger_value} inch"
                else:
                    original_size = ''

                artwork_entry = db.session.query(Artwork).filter_by(uuid=uuid).scalar()
                artwork_entry_id = artwork_entry.id
                artwork_entry.product_title = product_title
                artwork_entry.short_description = short_description
                artwork_entry.long_description = long_description
                artwork_entry.creation_year = year
                artwork_entry.medium = medium
                artwork_entry.surface = surface
                artwork_entry.original_size = original_size
                artwork_entry.original_available = original_available
                artwork_entry.original_price = original_price
                artwork_entry.original_discount_percentage = original_discount_percent
                artwork_entry.print = sell_prints
                artwork_entry.limited_print_count = limited_print_count
                artwork_entry.recreation = recreation
                artwork_entry.limited_recreation_count = limited_recreation_count
                db.session.commit()

                if original_available == 'available':
                    if len([e for e in artwork_entry.variants if e.artwork_id == artwork_entry.id]) == 0:
                        existing_variant_uuid_list = []
                        variants = db.session.query(ArtworkVariants).all()
                        for v in variants:
                            existing_variant_uuid_list.append(v.uuid)
                        variant_uuid = create_uuid(existing_variant_uuid_list, 8)
                        entry = ArtworkVariants(
                            category='original',
                            subcategory='Original',
                            medium=medium,
                            surface=surface,
                            size=original_size,
                            price=original_price,
                            discount_percent=original_discount_percent,
                            artwork_id=artwork_entry_id,
                            uuid=variant_uuid,
                            thumbnail_path=artwork_entry.main_photo_path
                        )
                        db.session.add(entry)
                        db.session.commit()
                form_name = 'variants'
                step_1 = 'done'
                p(f"Form name :{form_name}")
                return redirect(url_for('artist_dashboard_operations.edit_artwork_prints', uuid=uuid))
                return render_template('pending_artwork_details_edit.html',artwork_details_dict=artwork_details_dict, pending_details_artworks_dict=pending_details_artworks_dict, 
                                    pending_artwork_count=pending_artwork_count, form_name=form_name, step_1=step_1, step_2=step_2, logged_in=current_user.is_authenticated, current_year=current_year, admin=admin)
            if request.form.get('submit') == 'submit-artwork-images':
                additional_image_path_list = []
                artwork_uuid = request.form.get('artwork_uuid')
                additional_thumbnail_path = f"static/files/users/{current_user.uuid}/artworks/spiritual/{artwork_uuid}/additional_images/"
                temp_thumbnail_path = f"./static/files/users/{current_user.uuid}/temp/temp_thumbnails/"
                temp_original_file_path_base = f"./static/files/users/{current_user.uuid}/temp/artwork/"
                if not os.path.exists(additional_thumbnail_path):
                    os.makedirs(additional_thumbnail_path)
                    
                # 1. Check if the file part is present in the request
                if 'artwork-additional-images' not in request.files:
                    return jsonify({'error': 'No file part in the request'}), 400
                    
                files = request.files.getlist('artwork-additional-images')
                # 2. Check if the user submitted an empty form without selecting a file
                for f in files:
                    if f.filename == '':
                         jsonify({'error': 'No file selected'}), 400
                    filename = secure_filename(f.filename)
                    temp_original_file_path = temp_original_file_path_base+filename
                    f.save(temp_original_file_path)
                    file_path = create_thumbnail_single(temp_original_file_path, temp_thumbnail_path, 900)[0]
                    webp_thumbnail_filepath = '/' + single_png_jpg_to_webp(file_path, additional_thumbnail_path, quality=100)[0]
                    additional_image_path_list.append(webp_thumbnail_filepath)

                    os.remove(temp_original_file_path)
                    os.remove(file_path)

                artwork = db.session.query(Artwork).filter_by(uuid=artwork_uuid).scalar()
                existing_additional_img_path_list = json.loads(artwork.additional_photo_paths)
                for path in existing_additional_img_path_list:
                    additional_image_path_list.append(path)
                artwork.additional_photo_paths = json.dumps(additional_image_path_list)
                db.session.commit()
                p('Additional file paths successfully added to database')
                    
        return render_template('pending_artwork_details_edit.html', logged_in=current_user.is_authenticated, current_year=current_year, admin=admin,
                            artwork_details_dict=artwork_details_dict, form_name=form_name, step_1=step_1, step_2=step_2, pending_details_artworks_dict=pending_details_artworks_dict, pending_artwork_count=pending_artwork_count,
                            photo_size_list=photo_size_list, canvas_size_list=canvas_size_list)
    else:
        return redirect(url_for('account.login', instruction='Login to Continue'))


@artist_dashboard_operations.route('/edit_artwork_prints', methods=['GET', 'POST'])
def edit_artwork_prints():
    pending_details_artworks_uuid_list = []
    pending_details_artworks_dict = {}
    existing_variant_btn_value_list = []
    if request.method == 'POST' and request.is_json:
        data = request.get_json()
        uuid = data
        session['uuid'] = uuid
        return jsonify({"redirect_url": url_for('artist_dashboard_operations.edit_artwork_prints')})

    artwork_uuid = request.args.get('uuid')
    if not artwork_uuid:
        artwork_uuid = session.get('uuid')
    artwork = db.session.query(Artwork).filter_by(uuid=artwork_uuid).scalar()
    artwork_variants = artwork.variants
    for v in artwork_variants:
        if v.subcategory == 'Photo':
            existing_variant_btn_value_list.append('Photo-'+v.size)
        elif v.subcategory == 'Canvas':
            existing_variant_btn_value_list.append('Canvas-'+v.size)

    admin = db.session.query(Role).filter_by(name='admin').scalar()
    artwork_title = artwork.title
    artwork_list = json.loads(artwork.print_size_list)
    a_size_list = artwork_list['a']
    photo_size_list = artwork_list['photo']
    canvas_size_list = artwork_list['canvas']
    artwork_hd_photo_path = artwork.hd_photo_path
    artwork_dict = {'uuid': artwork_uuid, 'title': artwork_title, 'hd_photo_path': artwork_hd_photo_path}
    

    all_artworks = current_user.artworks
    for a in all_artworks:
        details = [a.theme, a.product_title, a.short_description, a.medium, a.original_price, a.original_available, a.creation_year, a.main_photo_path,
                    a.sale_status]
        if any(item is None for item in details):
            pending_details_artworks_uuid_list.append(a.uuid)
    for uuid in pending_details_artworks_uuid_list:
        a = db.session.query(Artwork).filter_by(uuid=uuid).scalar()
        artwork_title = a.title
        main_photo_path = a.main_photo_path
        uuid = a.uuid
        pending_details_artworks_dict[artwork_title] = {'main_photo_path': main_photo_path, 'uuid': uuid}
    pending_artwork_count = len(pending_details_artworks_dict)
    pending_details_artworks_dict = dict(reversed(pending_details_artworks_dict.items()))

    return render_template('edit_artwork_prints.html', logged_in=current_user.is_authenticated, current_year=current_year, admin=admin, photo_size_list=photo_size_list, canvas_size_list=canvas_size_list, artwork_dict=artwork_dict,
                           pending_details_artworks_dict=pending_details_artworks_dict, pending_artwork_count=pending_artwork_count, artwork_uuid=artwork_uuid, existing_variant_btn_value_list=existing_variant_btn_value_list)


@artist_dashboard_operations.route('/save-print-variants', methods=['GET', 'POST'])
def save_print_variants():
    if request.method == 'POST' and request.is_json:
        data = request.get_json()
        img_data_url = data['image']
        artwork_uuid = data['artwork_uuid']
        price = data['price']
        print_category = data['category']
        print_size_inch = data['print_size_inch']
        print_width = float(print_size_inch.split(' ')[0])
        print_height = float(print_size_inch.split(' ')[2])
        print_ratio = print_width/print_height
        res = int(db.session.query(Tools).filter_by(keyword=print_size_inch).scalar().data.split('_')[1])
        print_width_px = print_width*res
        print_height_px = print_height*res

        if "," in img_data_url:
            header, base64_data = img_data_url.split(",", 1)
        else:
            base64_data = img_data_url

        image_bytes = base64.b64decode(base64_data)
        image_buffer = BytesIO(image_bytes)

        img = Image.open(image_buffer)
        img_width = img.width
        img_height = img.height
        img_ratio = img_width/img_height

        if img_ratio > 1: # means img is landscape
            if print_ratio < 1: # means print is portrait
                new_width = print_height_px
                new_height = print_width_px
            else:
                new_width = print_width_px
                new_height = print_height_px
        else: # means img is portrait
            if print_ratio > 1: # means print is landscape
                new_width = print_height_px
                new_height = print_width_px
            else:
                new_width = print_width_px
                new_height = print_height_px

        resized_img = img.resize((round(new_width), round(new_height)), Image.Resampling.LANCZOS)
        img_save_path = f"./static/files/users/{current_user.uuid}/artworks/spiritual/{artwork_uuid}/variants/print/original/"
        if not os.path.exists(img_save_path):
            os.makedirs(img_save_path)
        artwork_title = db.session.query(Artwork).filter_by(uuid=artwork_uuid).scalar().title
        img_name = f"{current_user.uuid}_$_print_$_{print_category}_$_{print_size_inch}_$_{artwork_title}.png"
        resized_img.save(img_save_path+img_name, compress_level=6, optimize=True)
        original_file_path = img_save_path+img_name
        temp_thumbnail_path = f"./static/files/users/{current_user.uuid}/temp/temp_thumbnails/"
        variant_thumbnail_save_path = f"./static/files/users/{current_user.uuid}/artworks/spiritual/{artwork_uuid}/variants/print/thumbnail/"
        if not os.path.exists(temp_thumbnail_path):
            os.makedirs(temp_thumbnail_path)
        if not os.path.exists(variant_thumbnail_save_path):
            os.makedirs(variant_thumbnail_save_path)

# CREATE THUMBNAIL AND THEN CONVERTS IT INTO WEBP ----------------------------------------------------------
        file_path = create_thumbnail_single(original_file_path, temp_thumbnail_path, 900)[0]
        webp_thumbnail_filepath = single_png_jpg_to_webp(file_path, variant_thumbnail_save_path, quality=100)[0][1:]

        os.remove(file_path)

# Checks whether the variant already exists, if yes, it updates just the price and photo, if not then created variant anew.#
        artwork = db.session.query(Artwork).filter_by(uuid=artwork_uuid).scalar()
        existing_print_variants = [p for p in artwork.variants if p.category == 'print']
        variants = db.session.query(ArtworkVariants).all()
        existing_uuid_list = [p.uuid for p in variants]
        variant_uuid = create_uuid(existing_uuid_list, 8)
        if len(existing_print_variants) == 0:
            artwork_id = artwork.id
            entry = ArtworkVariants(
                uuid=variant_uuid,
                category='print',
                subcategory=print_category,
                size=print_size_inch,
                price=price,
                artwork_id=artwork_id,
                photo_for_print=original_file_path[1:],
                thumbnail_path=webp_thumbnail_filepath
            )
            db.session.add(entry)
            db.session.commit()
        else:
            match_found = ''
            matching_variant_uuid = ''
            for v in existing_print_variants:
                if v.subcategory == print_category and v.size == print_size_inch:
                    matching_variant_uuid = v.uuid
                    match_found = 'positive'

            if match_found == 'positive':
                db.session.query(ArtworkVariants).filter_by(uuid=matching_variant_uuid).scalar().price = price
                db.session.commit()
            else:
                artwork_id = artwork.id
                entry = ArtworkVariants(
                    uuid=variant_uuid,
                    category='print',
                    subcategory=print_category,
                    size=print_size_inch,
                    price=price,
                    artwork_id=artwork_id,
                    photo_for_print=original_file_path[1:],
                    thumbnail_path=webp_thumbnail_filepath
                )
                db.session.add(entry)
                db.session.commit()

    return '', 204