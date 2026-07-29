import pprint
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, send_file
import os
import random
from flask_login import current_user
from werkzeug.utils import secure_filename
from extensions import db, current_year, list_files_in_directory, list_folders_in_directory, p
from models.member import Member, Portrait, Role
from models.artwork import *
from operations.miscellaneous import allowed_file, text_match
from operations.artist_tools import add_watermark, delete_single_watermarked_image, delete_all_from_user
from models.artist_data import ArtistData
from pathlib import Path, PureWindowsPath
from models.tool import ArtworkPriceTime
import json
from babel.numbers import format_currency

studio = Blueprint('studio', __name__, static_folder="static", template_folder='templates/studio/')


@studio.route('/', methods=['GET', 'POST'])
def home():
    admin = db.session.query(Role).filter_by(name='admin').scalar()
    artwork_dict = {}

    all_artworks = db.session.query(Artwork).all()
    for a in all_artworks:
        variants = a.variants
        active_variants = [a for a in variants if a.status == 'active']
        if (a.original_available == 'available' and a.sale_status != 'sold') or len(active_variants) > 0:
            product_title = a.product_title
            main_photo_path = a.main_photo_path
            artist_name = a.artist.name
            artwork_dict[a.uuid] = {
                'product_title': product_title,
                'main_photo_path': main_photo_path,
                'artist_name': artist_name
            }
    return render_template('studio.html', current_year=current_year, logged_in=current_user.is_authenticated, admin=admin,
                           artwork_dict=artwork_dict)


@studio.route('/artists', methods=['GET', 'POST'])
def artists():
    admin = db.session.query(Role).filter_by(name='admin').scalar()
    members = []
    result = db.session.query(Member).all()
    for member in result:
        members.append(member)
        # print(member.sex)

    if request.method == 'POST':

        member_uuid = request.form.get('uuid')
        member = db.session.query(Member).filter_by(uuid=member_uuid).one()

        return redirect(url_for('studio.portfolio', member_uuid=member_uuid))
    return render_template('artists.html', members=members, current_year=current_year, logged_in=current_user.is_authenticated, admin=admin)


@studio.route('/portfolio/<member_uuid>')
def portfolio(member_uuid):
    admin = db.session.query(Role).filter_by(name='admin').scalar()
    member_uuid = member_uuid
    member = db.session.query(Member).filter_by(uuid=member_uuid).scalar()
    artist_name = member.name
    artist_dict = {}
    artworks_thumbnail_dir = f'static/files/users/{member_uuid}/artworks/spiritual/thumbnail/'
    artworks_large_dir = f'static/files/users/{member_uuid}/artworks/spiritual/large/'
    if not os.path.exists(artworks_thumbnail_dir):
        os.makedirs(artworks_thumbnail_dir)
    if not os.path.exists(artworks_large_dir):
        os.makedirs(artworks_large_dir)
    
    index = 1
    artworks_thumbnail_list = [f for f in Path(artworks_thumbnail_dir).iterdir() if f.is_file()]
    for entry in artworks_thumbnail_list:
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
    profile_pic_url = f"/static/files/users/{member_uuid}/profile/profile-pic.jpg"
    return render_template('portfolio.html',artist_name=artist_name, dict=artist_dict, profile_pic_url=profile_pic_url, current_year=current_year, logged_in=current_user.is_authenticated, admin=admin)


@studio.route('/artist_tools', methods=['GET', 'POST'])
def artist_tools():
    admin = db.session.query(Role).filter_by(name='admin').scalar()
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
                           logged_in=current_user.is_authenticated, total_watermarked=total_watermarked_photos, current_year=current_year, admin=admin)

@studio.route('/portraits', methods=['GET', 'POST'])
def portraits():
    admin = db.session.query(Role).filter_by(name='admin').one_or_none()
    artwork_dict = {}

    base_path = 'static/files/users/477706/artworks/portrait/thumbnail'
    dir_path = Path(base_path)
    all_portrait_files = [str(f) for f in dir_path.iterdir() if f.is_file()]
    for f in all_portrait_files:
        title_raw = PureWindowsPath(f).name
        path = f
        uuid = title_raw.split('.')[0].split('-')[1].split('_')[0]
        artist = db.session.query(Portrait).filter_by(uuid=uuid).scalar().artist
        title = title_raw.split('.')[0].split('-')[0].replace('_', ' ')
        artwork_dict[uuid] = {'title': title, 'path': path, 'artist': artist}

        items = list(artwork_dict.items())
        random.shuffle(items)

        artwork_dict = dict(items)

        # Finding maximum discount from database to display on the discount advertisement--------------------
        discount_list = []
        data = db.session.query(ArtworkPriceTime).all()
        for discount in data:
            discount_list.append(discount.discount_percentage)
        maximum_discount = max(discount_list)


    return render_template('portraits.html', logged_in=current_user.is_authenticated, artwork_dict=artwork_dict,
                           admin=admin, maximum_discount=maximum_discount)


@studio.route('/portrait-detail', methods=['GET', 'POST'])
def portrait_detail():
    admin = db.session.query(Role).filter_by(name='admin').one_or_none()
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
    artist = portrait.artist_name

    portrait_price_time_dict = {}
    data = db.session.query(ArtworkPriceTime).all()
    for entry in data:
        price = f"{entry.price:,}"
        discounted_price = ((100 - entry.discount_percentage)/100) * entry.price
        discounted_price = f"{int(discounted_price):,}"

        portrait_price_time_dict[entry.type] = {
            'price': price,
            'discount_percentage': entry.discount_percentage,
            'discounted_price': discounted_price,
            'time_taken': entry.time_taken
        }
    return render_template('portrait-detail.html', img_path=img_path, title=title, description=description,
                           medium=medium, artist=artist, logged_in=current_user.is_authenticated, admin=admin,
                           portrait_price_time_dict=portrait_price_time_dict)


@studio.route('/artwork-product', methods=['GET', 'POST'])
def artwork_product():
    admin = db.session.query(Role).filter_by(name='admin').scalar()

    additional_img_path_list = []
    artwork_uuid = request.args.get('artwork_uuid')
    artwork = db.session.query(Artwork).filter_by(uuid=artwork_uuid).scalar()
    main_img_path = artwork.main_photo_path
    if artwork.additional_photo_paths:
        additional_img_path_list = json.loads(artwork.additional_photo_paths)
    additional_img_path_list.append(main_img_path)
    additional_img_path_list.reverse()
    product_title = artwork.product_title
    short_description = artwork.short_description
    long_description = artwork.long_description
    theme = artwork.theme
    rating = artwork.net_rating
    if not rating:
        rating = 0
    artist_name = artwork.artist.name
    original_size = artwork.original_size
    original_price = artwork.original_price
    original_discount_percent = artwork.original_discount_percentage
    if original_discount_percent:
        original_discount_percent = int(original_discount_percent)
    else:
        original_discount_percent = 0
    original_medium = artwork.medium
    original_surface = artwork.surface
    original_medium_surface = original_medium + ' on ' + original_surface
    category_list = []
    if len([v for v in artwork.variants if v.category == 'print' and v.status == 'active']) > 0 and artwork.print == 'yes':
        category_list.append(('print', 'Prints'))
        
    if len([v for v in artwork.variants if v.category == 'print' and v.status == 'active']) > 0 and artwork.print == 'limited':
            category_list.append(('print', 'Limited prints'))
    if len([v for v in artwork.variants if v.category == 'recreation' and v.status == 'active']) > 0 and artwork.recreation == 'yes':
        category_list.append(('recreation', 'Recreations'))
    if len([v for v in artwork.variants if v.category == 'recreation' and v.status == 'active']) > 0 and artwork.recreation == 'limited':
            category_list.append(('recreation', 'Limited recreations'))
    if len([v for v in artwork.variants if v.category == 'original' and v.status == 'active']) > 0:
            category_list.append(('original', 'Original'))
    category_count = len(category_list)
    count = 1
    category_text = ''
    for c in category_list:
        if count == 1:
            category_text = c[1]
        elif count < category_count:
            category_text = category_text + ", " + c[1]
        else:
            category_text = category_text + ' and ' + c[1]
        count += 1

    # size_dict = json.loads(artwork.print_size_list)
    # photo_sizes = size_dict['photo']
    # canvas_sizes = size_dict['canvas']
    print_variants = {}
    recreation_variants = {}
    artwork_variants = artwork.variants
    for v in artwork_variants:
        if v.category == 'print':
            if v.discount_percent:
                discount_percent = int(v.discount_percent)
            else:
                discount_percent = 0
            print_variants[v.uuid] = {
                'uuid': v.uuid,
                'category': v.category,
                'subcategory': v.subcategory,
                'medium': v.medium,
                'surface': v.surface,
                'size': v.size,
                'price': v.price,
                'discount_percent': discount_percent,
                'inventory': v.inventory,
                'delivery_charge': v.delivery_charge,
                'urgent_charge_percentage': v.urgent_charge_percentage,
                'delivered_as': v.delivered_as,
                'display_img_path': v.thumbnail_path
            }
        elif v.category == 'recreation':
            if v.discount_percent:
                discount_percent = int(v.discount_percent)
            else:
                discount_percent = 0
            recreation_variants[v.uuid] = {
                'uuid': v.uuid,
                'category': v.category,
                'subcategory': v.subcategory,
                'medium': v.medium,
                'surface': v.surface,
                'size': v.size,
                'price': v.price,
                'discount_percent': discount_percent,
                'inventory': v.inventory,
                'delivery_charge': v.delivery_charge,
                'urgent_charge_percentage': v.urgent_charge_percentage,
                'delivered_as': v.delivered_as,
                'display_img_path': v.thumbnail_path
            }
    artwork_dict = {
        'artwork_uuid': artwork_uuid,
        'main_img_path': main_img_path,
        'additional_img_path_list': additional_img_path_list,
        'product_title': product_title,
        'short_description': short_description,
        'long_description': long_description,
        'theme': theme,
        'rating': rating,
        'artist_name': artist_name,
        'category': category_text,
        'category_count': category_count,
        'product_type': category_list,
        'original_size': original_size,
        'original_medium_surface': original_medium_surface,
        'original_price': original_price,
        'original_discount_percentage': int(original_discount_percent)
    }
    photo_variant_count = len([a for a in artwork_variants if a.subcategory == 'Photo' and a.status == 'active'])
    canvas_variant_count = len([a for a in artwork_variants if a.subcategory == 'Canvas' and a.status == 'active'])
    all_variant_count = photo_variant_count+canvas_variant_count
    if artwork.original_available == 'available' and artwork.sale_status != 'sold':
        original = 'yes'
    else:
        original = 'no'
    product_url = url_for('studio.artwork_product')
    return render_template('artwork_product.html', logged_in=current_user.is_authenticated, admin=admin, product_url=product_url, artwork_dict=artwork_dict,
                           print_variants=print_variants, recreation_variants=recreation_variants, photo_variant_count=photo_variant_count, canvas_variant_count=canvas_variant_count, all_variant_count=all_variant_count, original=original)


@studio.route('/artwork-pricing', methods=['GET', 'POST'])
def artwork_pricing():
    admin = db.session.query(Role).filter_by(name='admin').one_or_none()
    example_base_charge = 0

    portrait_price_time_dict = {}
    data = db.session.query(ArtworkPriceTime).all()
    for entry in data:
        price = f"{entry.price:,}"
        discounted_price = ((100 - entry.discount_percentage) / 100) * entry.price
        if entry.type == 'portrait_oil_on_canvas_36x48':
            example_base_charge += discounted_price
        discounted_price = f"{int(discounted_price):,}"

        portrait_price_time_dict[entry.type] = {
            'price': price,
            'discount_percentage': entry.discount_percentage,
            'discounted_price': discounted_price,
            'time_taken': entry.time_taken
        }

    additional_price = int(.3 * example_base_charge)
    print(additional_price)
    total_price = int(example_base_charge + additional_price)
    return render_template('artwork-pricing.html', logged_in=current_user.is_authenticated, admin=admin,
                           portrait_price_time_dict=portrait_price_time_dict, additional_price=additional_price,
                           total_price=total_price)


