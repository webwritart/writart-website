from pathlib import PureWindowsPath
import random
from flask import Blueprint, render_template, request, flash, session, url_for
from extensions import login_manager, db, current_year, list_files_in_directory, p
from models.member import Member, Workshop, Role, Certificate
from models.query import Query
from models.tool import Tools, ArtworkPriceTime
from flask_login import current_user
from operations.miscellaneous import *
from models.artist_data import *
from operations.artist_tools import delete_watermarked_images
from operations.miscellaneous import image_resize_and_compress_single
import io

main = Blueprint('main', __name__, static_folder='static', template_folder='templates')


@main.route('/', methods=['GET', 'POST'])
def home():
    session['url'] = url_for('main.home')
    admin = db.session.query(Role).filter_by(name='admin').one_or_none()
    client = db.session.query(Role).filter_by(name='client').one_or_none()
    animation_admin = db.session.query(Role).filter_by(name='animation_admin').one_or_none()
    # ---------------------------------------- Main ----------------------------------------------------- #
    portrait_folder = 'static/files/users/477706/artworks/portrait/large/'
    portrait_list = []

    for file in list_files_in_directory(portrait_folder):
        portrait_list.append(PureWindowsPath(file))
    random.shuffle(portrait_list)

    # Finding maximum discount from database to display on the discount advertisement--------------------
    discount_list = []
    data = db.session.query(ArtworkPriceTime).all()
    for discount in data:
        discount_list.append(discount.discount_percentage)
    maximum_discount = max(discount_list)

    return render_template('index.html', logged_in=current_user.is_authenticated, admin=admin, client=client,
                           animation_admin=animation_admin, portrait_list=portrait_list, maximum_discount=maximum_discount)


@main.route('/privacy_policy')
def privacy_policy():
    return render_template('privacy_policy.html', current_year=current_year)


@main.route('/verification', methods=['GET', 'POST'])
def verification():
    if request.method == 'POST':
        if request.form.get('submit') == 'verify-certificate':
            certificate_id = request.form.get('certificate-id')

            student_dict = {}

            certificate_no_list = []
            all_certificates = db.session.query(Certificate).all()
            for c in all_certificates:
                certificate_no_list.append(c.certificate_no)
            
            if certificate_id in certificate_no_list:
                certificate = db.session.query(Certificate).filter_by(certificate_no=int(certificate_id)).scalar()
                course_topic = certificate.course_topic
                course_period = certificate.course_period
                session_type = certificate.session_type
                instructor = certificate.instructor
                issue_date = certificate.issue_date
                awardee_name = certificate.awardee_name

                student_dict[certificate_id] = {
                    'course_topic': course_topic,
                    'course_period': course_period,
                    'session_type': session_type,
                    'instructor': instructor,
                    'issue_date': issue_date,
                    'awardee_name': awardee_name
                }
                return render_template('certificate_verification_details.html', current_year=current_year, dict=student_dict, status='success', logged_in=current_user.is_authenticated)
            else:
                return render_template('certificate_verification_details.html', current_year=current_year, status='failed', logged_in=current_user.is_authenticated)
    return render_template('verification.html', logged_in=current_user.is_authenticated, current_year=current_year)


@main.route('/temp', methods=['GET', 'POST'])
def temp():
    print_width = 4
    print_height = 6
    print_ratio = print_width/print_height
    res = 300
    print_width_px = print_width*res
    print_height_px = print_height*res
    if request.method == 'POST' and request.is_json:
        img_data = request.get_json()
        img_data_url = img_data['image']
        if "," in img_data_url:
            header, base64_data = img_data_url.split(",", 1)
        else:
            base64_data = img_data_url

        image_bytes = base64.b64decode(base64_data)

        image_buffer = io.BytesIO(image_bytes)
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

        resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        img_save_path = "./static/files/users/477706/temp/artwork/"
        img_name = 'test.jpg'
        resized_img.save(img_save_path+img_name, compress_level=0)
    return render_template('temp.html')


@main.route('/qr_verification', methods=['GET', 'POST'])
def qr_verification():
    token = request.args.get('token')
    category = request.args.get('category')
    if category == 'coa':
        coa_data = db.session.query(Coa).filter_by(serial_no=token).scalar()
        coa_dict = {
            'Serial No':coa_data.serial_no,
            'Title':coa_data.title,
            'Artist':coa_data.artist_name,
            'Size':coa_data.size,
            'Medium':coa_data.medium,
            'Year':coa_data.year,
            'Client Name':coa_data.client_name,
            'Date Issued':coa_data.issue_date
        }
        return render_template('qr_verification.html', logged_in=current_user.is_authenticated, current_year=current_year,
                            category=category, coa_dict=coa_dict)
        
    return render_template('qr_verification.html', logged_in=current_user.is_authenticated, current_year=current_year)


