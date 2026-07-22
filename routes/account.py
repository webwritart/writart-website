import os
from flask import Blueprint, render_template, request, flash, send_file, redirect, url_for, session
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
from models.transactions import *
from routes import main
import random
from io import BytesIO
from zipfile import ZipFile, ZIP_DEFLATED
import shutil
from pathlib import Path


account = Blueprint('account', __name__, static_folder='static', template_folder='templates/account')

otp = []
today_date = date.today()


@login_required
@account.route('/', methods=['GET', 'POST'])
def home():
    admin = db.session.query(Role).filter_by(name='admin').one_or_none()
    client = db.session.query(Role).filter_by(name='client').one_or_none()
    animation_admin = db.session.query(Role).filter_by(name='animation_admin').one_or_none()
    if current_user.is_authenticated:
        if len(current_user.participated) > 0:
            certificate = True
        else:
            certificate = False

        if request.method == 'POST':
            if request.form.get('whatsapp'):
                current_user.whatsapp = request.form.get("whatsapp")
            if request.form.get('profession'):
                current_user.profession = request.form.get("profession")
            if request.form.get('name'):
                current_user.name = request.form.get("name")
            if request.form.get('state'):
                current_user.state = request.form.get('state')
            if request.form.get('phone'):
                phone = request.form.get('phone')
                result = db.session.execute(db.select(Member).where(Member.phone == phone))
                user = result.scalar()
                if user:
                    flash("Couldn't update number as there's already an account with this number", category="error")
                else:
                    current_user.phone = request.form.get("phone")
            if request.form.get('email'):
                mail_ = request.form.get('email')
                result2 = db.session.execute(db.select(Member).where(Member.email == mail_))
                user2 = result2.scalar()
                if user2:
                    flash("Couldn't update email as there's already an account with this email", category="error")
                else:
                    current_user.email = request.form.get("email")

            if request.form.get('old-pwd'):
                old_pwd = request.form.get('old-pwd')
                if not check_password_hash(current_user.password, old_pwd):
                    flash("Please enter the correct old password", category="error")
                else:
                    hash_and_salted_password = generate_password_hash(
                        request.form.get('new-pwd'),
                        method='pbkdf2:sha256',
                        salt_length=8
                    )
                    current_user.password = hash_and_salted_password
                    db.session.commit()
                    flash("Password changed successfully", category="success")
            if request.form.get('fb-url'):
                if 'https://' not in request.form.get('fb-url'):
                    fb_url = 'https://' + request.form.get('fb-url')
                else:
                    fb_url = request.form.get('fb-url')
                current_user.fb_url = fb_url
            if request.form.get('insta-url'):
                if 'https://' not in request.form.get('insta-url'):
                    insta_url = 'https://' + request.form.get('insta-url')
                else:
                    insta_url = request.form.get('fb-url')
                current_user.insta_url = insta_url
            if request.form.get('web-url'):
                if 'https://' not in request.form.get('web-url'):
                    website = 'https://' + request.form.get('web-url')
                else:
                    website = request.form.get('web-url')
                current_user.website = website

            db.session.commit()

            if request.form.get('submit') == 'download-certificate':
                folder_name = current_user.name.split()[0] + str(current_user.id)
                last_workshop_name = current_user.participated[len(current_user.participated) - 1].name
                second_last_workshop_name = current_user.participated[len(current_user.participated) - 2].name
                topic = current_user.participated[len(current_user.participated) - 1].topic
                topic2 = current_user.participated[len(current_user.participated) - 2].topic
                file_name = f"{last_workshop_name}-{current_user.name.split()[0]}.pdf"
                file_name_2 = f"{second_last_workshop_name}-{current_user.name.split()[0]}.pdf"
                path = f"../static/files/users/{folder_name}/certificates/{file_name}"
                path2 = f"../static/files/users/{folder_name}/certificates/{file_name_2}"
                if os.path.exists(path):
                    return send_file(path_or_file=path, as_attachment=True,
                                     download_name=f"Certificate - {topic} - Writart Gurukul.pdf")
                elif os.path.exists(path2):
                    return send_file(path_or_file=path2, as_attachment=True,
                                     download_name=f"Certificate - {topic2} - Writart Gurukul.pdf")
                else:
                    flash('The Certificate is to be uploaded soon!', 'error')

            topic_list = []
            result = current_user.participated
            for r in result:
                topic_list.append(r.topic)
            if request.form.get('submit') in topic_list:
                index = topic_list.index(request.form.get('submit'))
                ws = db.session.query(Workshop).filter_by(topic=topic_list[index]).one()
                folder_name = current_user.name.split()[0] + str(current_user.id)
                file_name = f"{ws.name}-{current_user.name.split()[0]}.pdf"
                path = f"../static/files/users/{folder_name}/certificates/{file_name}"
                return send_file(path_or_file=path, as_attachment=True,
                                 download_name=f"Certificate - {topic_list[index]} - Writart Gurukul.pdf")

            if request.form.get('submit') == 'DELETE-ACCOUNT':
                user = current_user
                password = request.form.get('password')
                confirmation = request.form.get('confirmation')
                feedback = request.form.get('message')
                if confirmation == 'DELETE' or confirmation == "'DELETE'":
                    if check_password_hash(user.password, password):
                        message = f'Dear Admin\n\nThe user below has requested their account deletion\n\nUser name: {user.name}' \
                                  f'\nUser_ID: {user.id}\nEmail: {user.email}\nPhone: {user.phone}\nMessage: {feedback}'
                        send_email_support('Account Deletion Request', ['writartstudios@gmail.com'], message, '', '')
                        flash(
                            "Your account deletion request successfully submitted to the Admin! Your account will be deleted "
                            "soon!", "success")
                        return redirect(url_for('account.home'))
                    else:
                        flash("Wrong password! Please try again!", "error")
                else:
                    flash("Wrong word! Type only 'DELETE' in the box!", "error")

            return redirect(url_for('account.home'))

        certificate_list = []
        if len(current_user.participated) > 0:
            for workshop in current_user.participated:
                file_name = f"{workshop.name}-{current_user.name.split()[0]}.pdf"
                folder_name = current_user.name.split()[0] + str(current_user.id)
                path = f"../static/files/users/{folder_name}/certificates/{file_name}"
                if os.path.exists(path):
                    certificate_list.append(workshop.topic)

        role_result = current_user.role
        roles = []
        for role in role_result:
            roles.append(role.name)
        if 'admin' in roles:
            roles.remove('admin')
        
        role_count = len(roles)

        return render_template('my_account.html', certificate_list=certificate_list, certificate=certificate,
                               name=current_user.name, logged_in=current_user.is_authenticated, admin=admin,
                               client=client,
                               animation_admin=animation_admin, roles=roles, role_count=role_count, current_year=current_year)
    else:
        return render_template('my_account.html', current_year=current_year)



@account.route('/main-dashboard', methods=['GET', 'POST'])
def main_dashboard():
    if not current_user.is_authenticated:
        return redirect(url_for('account.login'))
    admin = db.session.query(Role).filter_by(name='admin').scalar()
    student = db.session.query(Role).filter_by(name='student').scalar()
    artist = db.session.query(Role).filter_by(name='artist').scalar()
    instructor = db.session.query(Role).filter_by(name='instructor').scalar()

    roles = current_user.role

    if len(roles) == 1:
        if student in roles:
            return redirect(url_for('account.student_dashboard', logged_in=current_user.is_authenticated, current_year=current_year))

    return render_template('main_dashboard.html', logged_in=current_user.is_authenticated, current_year=current_year, admin=admin,
                           artist=artist, instructor=instructor, student=student)



@account.route('/student-dashboard', methods=['GET', 'POST'])
def student_dashboard():
    if not current_user.is_authenticated:
        return redirect(url_for('account.login'))

    multiple_roles = False
    roles = current_user.role
    admin = db.session.query(Role).filter_by(name='admin').scalar()
    artist = db.session.query(Role).filter_by(name='artist').scalar()
    instructor = db.session.query(Role).filter_by(name='instructor').scalar()
    if len(roles) > 1:
        multiple_roles = True

    # --------------------------------------------- News --------------------------------------------------------------------- #
    date_time_list = []
    school_news_dict = {}
    common_news_dict = {}
    month_list = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    school_news = db.session.query(News).filter_by(category='school').all()
    for news in school_news:
        date_time = news.date_time
        date_time_list.append(date_time)
    sorted_dates = sorted(date_time_list, key=lambda d: datetime.strptime(d, "%Y-%m-%d %H:%M:%S"), reverse=True)
    for item in sorted_dates:
        news = db.session.query(News).filter_by(date_time=item).scalar()
        news_text = news.text
        news_link = news.link
        news_date_raw = news.date_time.split(" ")[0].split('-')
        dt = news_date_raw[2]
        month = news_date_raw[1]
        year = news_date_raw[0]
        month_name = month_list[int(month)-1]
        news_date = f'{dt} {month_name}, {year}'
        school_news_dict[item] = {'news_text': news_text,'news_link': news_link, 'news_date': news_date}

    common_news = db.session.query(News).filter_by(category='common').all()
    date_time_list.clear()
    for n in common_news:
        date_time = n.date_time
        date_time_list.append(date_time)
    sorted_dates = sorted(date_time_list, key=lambda d: datetime.strptime(d, "%Y-%m-%d %H:%M:%S"), reverse=True)
    for item in sorted_dates:
        news = db.session.query(News).filter_by(date_time=item).scalar()
        news_text = news.text
        news_link = news.link
        news_date_raw = news.date_time.split(" ")[0].split('-')
        dt = news_date_raw[2]
        month = news_date_raw[1]
        year = news_date_raw[0]
        month_name = month_list[int(month) - 1]
        news_date = f'{dt} {month_name}, {year}'
        common_news_dict[item] = {'news_text': news_text, 'news_link': news_link, 'news_date': news_date}


    return render_template('student_dashboard.html', logged_in=current_user.is_authenticated, current_year=current_year,
                            school_news_dict=school_news_dict, common_news_dict=common_news_dict,
                           admin=admin, artist=artist, instructor=instructor, multiple_roles=multiple_roles)


@account.route('/artist-dashboard', methods=['GET', 'POST'])
def artist_dashboard():
    admin = db.session.query(Role).filter_by(name='admin').scalar()
    artist = db.session.query(Role).filter_by(name='artist').scalar()

    if request.method == 'POST':
        if request.form.get('submit') == 'create_document':
            document = request.form.get('document')
            name = request.form.get('name')
            billing_address = request.form.get('billing_address')
            billing_state = request.form.get('billing_state')
            billing_country = request.form.get('billing_country')
            billing_pincode = request.form.get('billing_pincode')
            shipping_address = request.form.get('shipping_address')
            shipping_state = request.form.get('shipping_state')
            shipping_country = request.form.get('shipping_country')
            shipping_pincode = request.form.get('shipping_pincode')
            shipping_same_as_billing = request.form.get('same_billing_shipping')
            phone = request.form.get('phone')
            email = request.form.get('email')
            item_count = int(request.form.get('item_count'))
            tax_percentage = request.form.get('tax_percentage')
            date_ = request.form.get('date')
            payment_type = request.form.get('payment_type')
            partial_payment_amount_paid = request.form.get('partial_payment_amount')
            receipt_invoice_no = request.form.get('receipt_invoice_no')

            if shipping_same_as_billing:
                shipping_address = billing_address
                shipping_state = billing_state
                shipping_country = billing_country
                shipping_pincode = billing_pincode

            if not date_:
                date_ = str(date.today())
        
            item_dict = {}

            for i in range(item_count):
                item_name = f'item{i+1}'
                item_price = f'{item_name}price'
                item_qty = f'{item_name}qty'
                item_n = request.form.get(item_name)
                item_p = request.form.get(item_price)
                item_q = request.form.get(item_qty)
                item_dict[i] = {
                    'item_description': item_n,
                    'price': item_p,
                    'qty': item_q
                }

            inv_receipt_data_dict = {
                'document': document,
                'name': name,
                'billing_address': billing_address,
                'billing_state': billing_state,
                'billing_country': billing_country,
                'billing_pincode': billing_pincode,
                'shipping_address': shipping_address,
                'shipping_state': shipping_state,
                'shipping_country': shipping_country,
                'shipping_pincode': shipping_pincode,
                'phone': phone,
                'email': email,
                'item_count': item_count,
                'tax_percentage': tax_percentage,
                'date': date_,
                'payment_type': payment_type,
                'partial_payment_amount_paid': partial_payment_amount_paid,
                'receipt_invoice_no': receipt_invoice_no,
                'item_dict': item_dict
            }
            session['inv_receipt_data_dict'] = inv_receipt_data_dict
            if document == '':
                flash('Aborted! Please select the document type first', 'error')
                return redirect(request.url)
            if document == 'invoice':
                if email:
                    customer_contact = email
                else:
                    customer_contact = phone
                document_state_country = f"{billing_state}, {billing_country}"
                result = prepare_invoice(name, document_state_country, customer_contact, item_dict, tax_percentage, date_, current_user.uuid)
                inv_preview_path = result[0]
                inv_pdf_path = result[1]
                inv_no = result[2]
                sub_total = result[3]
                grand_total = result[4]
                attachment_file_path = result[5]
                file_directory = result[6]

                session['invoice_preview_path'] = inv_preview_path
                session['invoice_pdf_path'] = inv_pdf_path
                session['invoice_no'] = inv_no
                session['sub_total'] = sub_total
                session['grand_total'] = grand_total
                session['attachment_path'] = attachment_file_path
                session['file_directory'] = file_directory

                return render_template('document_preview.html', preview_path=inv_preview_path, current_year=current_year, admin=admin, logged_in=current_user.is_authenticated, document='Invoice')
            
            elif document == 'receipt':
                if email:
                    customer_contact = email
                else:
                    customer_contact = phone
                document_state_country = f"{billing_state}, {billing_country}"
                result = prepare_receipt(name, document_state_country, customer_contact, item_dict, tax_percentage, date_, current_user.uuid, payment_type, partial_payment_amount_paid)
                rec_preview_path = result[0]
                rec_pdf_path = result[1]
                rec_no = result[2]
                sub_total = result[3]
                grand_total = result[4]
                attachment_file_path = result[5]
                file_directory = result[6]

                session['receipt_preview_path'] = rec_preview_path
                session['receipt_pdf_path'] = rec_pdf_path
                session['receipt_no'] = rec_no
                session['sub_total'] = sub_total
                session['grand_total'] = grand_total
                session['attachment_path'] = attachment_file_path
                session['file_directory'] = file_directory

                return render_template('document_preview.html', preview_path=rec_preview_path, current_year=current_year, admin=admin, logged_in=current_user.is_authenticated, document='Receipt')

        if request.form.get('submit') == 'save_email':
            # Save PDF of the Invoice ...........................................................................
            png_path = session.get('file_directory')
            pdf_export_path = session.get('invoice_pdf_path')
            png_to_pdf(png_path, pdf_export_path)

            # Add Customer to MEMBER table database............................................................
            existing_uuid_list = []
            all_members = db.session.query(Member).all()
            for m in all_members:
                existing_uuid_list.append(m.uuid)

            uuid = create_uuid(existing_uuid_list, 6)
            data_dict = session.get('inv_receipt_data_dict')
            if db.session.query(Member).filter_by(email=data_dict['email']).scalar():
                pass
            else:
                entry = Member(
                    uuid = uuid,
                    email=data_dict['email'],
                    name=data_dict['name'],
                    phone=data_dict['phone'],
                    billing_address=data_dict['billing_address'],
                    billing_state=data_dict['billing_state'],
                    billing_country=data_dict['billing_country'],
                    billing_pincode=data_dict['billing_pincode'],
                    shipping_address=data_dict['shipping_address'],
                    shipping_state=data_dict['shipping_state'],
                    shipping_country=data_dict['shipping_country'],
                    shipping_pincode=data_dict['shipping_pincode'],
                    registration_date = str(date.today()),
                )
                db.session.add(entry)
                db.session.commit()

            # Add Invoice details to database..................................................................
            item_dict = data_dict['item_dict']
            items_name = ''
            items_price = ''
            items_quantity = ''

            for i in item_dict:
                if items_name == '':
                    items_name = item_dict[i]['item_description']
                else:
                    items_name = f"{items_name}%{item_dict[i]['item_description']}"
                if items_price == '':
                    items_price = item_dict[i]['price']
                else:
                    items_price = f"{items_price}%{item_dict[i]['price']}"
                if items_quantity == "":
                    items_quantity = item_dict[i]['qty']
                else:
                    items_quantity = f"{items_quantity}%{item_dict[i]['qty']}"
            date_time = datetime.now().replace(microsecond=0)
            member_id = db.session.query(Member).filter_by(email=data_dict['email']).scalar().id

            entry = Invoice(
                invoice_no = session.get('invoice_no'),
                name=data_dict['name'],
                billing_address=data_dict['billing_address'],
                billing_state=data_dict['billing_state'],
                billing_country=data_dict['billing_country'],
                billing_pincode=data_dict['billing_pincode'],
                shipping_address=data_dict['shipping_address'],
                shipping_state=data_dict['shipping_state'],
                shipping_country=data_dict['shipping_country'],
                shipping_pincode=data_dict['shipping_pincode'],
                phone=data_dict['phone'],
                email=data_dict['email'],
                items_name=items_name,
                items_price=items_price,
                items_quantity=items_quantity,
                tax_percent=data_dict['tax_percentage'],
                sub_total=session.get('sub_total'),
                grand_total=session.get('grand_total'),
                status='Unpaid',
                date_time = date_time,
                member_id=member_id
            )
            db.session.add(entry)
            db.session.commit()

            # SEND EMAIL ..............................................................................
            subject = f"Invoice-{session.get('invoice_no')}"
            reply_back_email = 'shwetabhartist@gmail.com'
            recipients_list = [data_dict['email']]
            body = f"Dear {data_dict['name'].split(' ')[0]}\n\nPlease find the invoice attached!"
            attachment_file_path = session.get('attachment_path')
            send_email_with_pdf_attachment(subject, reply_back_email, recipients_list, body, attachment_file_path)
            flash('Saved and Mailed successfully', 'success')
            return redirect(request.url)
            

        elif request.form.get('submit') == 'save_download':
            # Save PDF of the Invoice ...........................................................................
            png_path = session.get('file_directory')
            pdf_export_path = session.get('invoice_pdf_path')
            filename = png_to_pdf(png_path, pdf_export_path)[0]

            # Add Customer to MEMBER table database............................................................
            existing_uuid_list = []
            all_students = db.session.query(Member).all()
            for s in all_students:
                existing_uuid_list.append(s.uuid)

            uuid = create_uuid(existing_uuid_list, 6)
            data_dict = session.get('inv_receipt_data_dict')
            if db.session.query(Member).filter_by(email=data_dict['email']).scalar():
                pass
            else:
                entry = Member(
                    uuid = uuid,
                    email=data_dict['email'],
                    name=data_dict['name'],
                    phone=data_dict['phone'],
                    billing_address=data_dict['billing_address'],
                    billing_state=data_dict['billing_state'],
                    billing_country=data_dict['billing_country'],
                    billing_pincode=data_dict['billing_pincode'],
                    shipping_address=data_dict['shipping_address'],
                    shipping_state=data_dict['shipping_state'],
                    shipping_country=data_dict['shipping_country'],
                    shipping_pincode=data_dict['shipping_pincode'],
                    registration_date = str(date.today()),
                )
                db.session.add(entry)
                db.session.commit()

            # Add Invoice details to database..................................................................
            item_dict = data_dict['item_dict']
            items_name = ''
            items_price = ''
            items_quantity = ''

            for i in item_dict:
                if items_name == '':
                    items_name = item_dict[i]['item_description']
                else:
                    items_name = f"{items_name}%{item_dict[i]['item_description']}"
                if items_price == '':
                    items_price = item_dict[i]['price']
                else:
                    items_price = f"{items_price}%{item_dict[i]['price']}"
                if items_quantity == "":
                    items_quantity = item_dict[i]['qty']
                else:
                    items_quantity = f"{items_quantity}%{item_dict[i]['qty']}"
            date_time = datetime.now().replace(microsecond=0)
            member_id = db.session.query(Member).filter_by(email=data_dict['email']).scalar().id

            entry = Invoice(
                invoice_no = session.get('invoice_no'),
                name=data_dict['name'],
                billing_address=data_dict['billing_address'],
                billing_state=data_dict['billing_state'],
                billing_country=data_dict['billing_country'],
                billing_pincode=data_dict['billing_pincode'],
                shipping_address=data_dict['shipping_address'],
                shipping_state=data_dict['shipping_state'],
                shipping_country=data_dict['shipping_country'],
                shipping_pincode=data_dict['shipping_pincode'],
                phone=data_dict['phone'],
                email=data_dict['email'],
                items_name=items_name,
                items_price=items_price,
                items_quantity=items_quantity,
                tax_percent=data_dict['tax_percentage'],
                sub_total=session.get('sub_total'),
                grand_total=session.get('grand_total'),
                status='Unpaid',
                date_time = date_time,
                member_id=member_id
            )
            db.session.add(entry)
            db.session.commit()
            # DOWNLOAD ................................................................................
            invoice_file_path = pdf_export_path + filename + '.pdf'
            return send_file(
                invoice_file_path,
                as_attachment=True,         # True forces a browser download prompt
                download_name=f"{filename}.pdf"  # Sets the default name for the downloaded file
            )
        elif request.form.get('submit') == 'save_email_download':
            # Save PDF of the Invoice ...........................................................................
            png_path = session.get('file_directory')
            pdf_export_path = session.get('invoice_pdf_path')
            filename = png_to_pdf(png_path, pdf_export_path)[0]

            # Add Customer to MEMBER table database............................................................
            existing_uuid_list = []
            all_students = db.session.query(Member).all()
            for s in all_students:
                existing_uuid_list.append(s.uuid)

            uuid = create_uuid(existing_uuid_list, 6)
            data_dict = session.get('inv_receipt_data_dict')
            if db.session.query(Member).filter_by(email=data_dict['email']).scalar():
                pass
            else:
                entry = Member(
                    uuid = uuid,
                    email=data_dict['email'],
                    name=data_dict['name'],
                    phone=data_dict['phone'],
                    billing_address=data_dict['billing_address'],
                    billing_state=data_dict['billing_state'],
                    billing_country=data_dict['billing_country'],
                    billing_pincode=data_dict['billing_pincode'],
                    shipping_address=data_dict['shipping_address'],
                    shipping_state=data_dict['shipping_state'],
                    shipping_country=data_dict['shipping_country'],
                    shipping_pincode=data_dict['shipping_pincode'],
                    registration_date = str(date.today()),
                )
                db.session.add(entry)
                db.session.commit()

            # Add Invoice details to database..................................................................
            item_dict = data_dict['item_dict']
            items_name = ''
            items_price = ''
            items_quantity = ''

            for i in item_dict:
                if items_name == '':
                    items_name = item_dict[i]['item_description']
                else:
                    items_name = f"{items_name}%{item_dict[i]['item_description']}"
                if items_price == '':
                    items_price = item_dict[i]['price']
                else:
                    items_price = f"{items_price}%{item_dict[i]['price']}"
                if items_quantity == "":
                    items_quantity = item_dict[i]['qty']
                else:
                    items_quantity = f"{items_quantity}%{item_dict[i]['qty']}"
            date_time = datetime.now().replace(microsecond=0)
            member_id = db.session.query(Member).filter_by(email=data_dict['email']).scalar().id

            entry = Invoice(
                invoice_no = session.get('invoice_no'),
                name=data_dict['name'],
                billing_address=data_dict['billing_address'],
                billing_state=data_dict['billing_state'],
                billing_country=data_dict['billing_country'],
                billing_pincode=data_dict['billing_pincode'],
                shipping_address=data_dict['shipping_address'],
                shipping_state=data_dict['shipping_state'],
                shipping_country=data_dict['shipping_country'],
                shipping_pincode=data_dict['shipping_pincode'],
                phone=data_dict['phone'],
                email=data_dict['email'],
                items_name=items_name,
                items_price=items_price,
                items_quantity=items_quantity,
                tax_percent=data_dict['tax_percentage'],
                sub_total=session.get('sub_total'),
                grand_total=session.get('grand_total'),
                status='Unpaid',
                date_time = date_time,
                member_id=member_id
            )
            db.session.add(entry)
            db.session.commit()

            # SEND EMAIL ..............................................................................
            subject = f"Invoice-{session.get('invoice_no')}"
            reply_back_email = 'shwetabhartist@gmail.com'
            recipients_list = [data_dict['email']]
            body = f"Dear {data_dict['name'].split(' ')[0]}\n\nPlease find the invoice attached!"
            attachment_file_path = session.get('attachment_path')
            send_email_with_pdf_attachment(subject, reply_back_email, recipients_list, body, attachment_file_path)

            # DOWNLOAD ................................................................................
            invoice_file_path = pdf_export_path + filename + '.pdf'
            return send_file(
                invoice_file_path,
                as_attachment=True,         # True forces a browser download prompt
                download_name=f"{filename}.pdf"  # Sets the default name for the downloaded file
            )
        if request.form.get('submit') == 'receipt-save-email':
            # Save PDF of the Receipt ...........................................................................
            png_path = session.get('file_directory')
            pdf_export_path = session.get('receipt_pdf_path')
            png_to_pdf(png_path, pdf_export_path)

            # Add Customer to MEMBER table database............................................................
            existing_uuid_list = []
            all_members = db.session.query(Member).all()
            for m in all_members:
                existing_uuid_list.append(m.uuid)

            uuid = create_uuid(existing_uuid_list, 6)
            data_dict = session.get('inv_receipt_data_dict')
            if db.session.query(Member).filter_by(email=data_dict['email']).scalar():
                pass
            else:
                entry = Member(
                    uuid = uuid,
                    email=data_dict['email'],
                    name=data_dict['name'],
                    phone=data_dict['phone'],
                    billing_address=data_dict['billing_address'],
                    billing_state=data_dict['billing_state'],
                    billing_country=data_dict['billing_country'],
                    billing_pincode=data_dict['billing_pincode'],
                    shipping_address=data_dict['shipping_address'],
                    shipping_state=data_dict['shipping_state'],
                    shipping_country=data_dict['shipping_country'],
                    shipping_pincode=data_dict['shipping_pincode'],
                    registration_date = str(date.today()),
                )
                db.session.add(entry)
                db.session.commit()

            # Add Receipt details to database..................................................................
            item_dict = data_dict['item_dict']
            items_name = ''
            items_price = ''
            items_quantity = ''

            for i in item_dict:
                if items_name == '':
                    items_name = item_dict[i]['item_description']
                else:
                    items_name = f"{items_name}%{item_dict[i]['item_description']}"
                if items_price == '':
                    items_price = item_dict[i]['price']
                else:
                    items_price = f"{items_price}%{item_dict[i]['price']}"
                if items_quantity == "":
                    items_quantity = item_dict[i]['qty']
                else:
                    items_quantity = f"{items_quantity}%{item_dict[i]['qty']}"
            date_time = datetime.now().replace(microsecond=0)
            member_id = db.session.query(Member).filter_by(email=data_dict['email']).scalar().id

            entry = Receipt(
                receipt_no=session.get('receipt_no'),
                name=data_dict['name'],
                billing_address=data_dict['billing_address'],
                billing_state=data_dict['billing_state'],
                billing_country=data_dict['billing_country'],
                billing_pincode=data_dict['billing_pincode'],
                shipping_address=data_dict['shipping_address'],
                shipping_state=data_dict['shipping_state'],
                shipping_country=data_dict['shipping_country'],
                shipping_pincode=data_dict['shipping_pincode'],
                phone=data_dict['phone'],
                email=data_dict['email'],
                items_name=items_name,
                items_price=items_price,
                items_quantity=items_quantity,
                tax_percent=data_dict['tax_percentage'],
                sub_total=session.get('sub_total'),
                grand_total=session.get('grand_total'),
                payment_type=data_dict['payment_type'],
                amount_paid=data_dict['partial_payment_amount_paid'],
                invoice_no=data_dict['receipt_invoice_no'],
                date_time = date_time,
                member_id=member_id
            )
            db.session.add(entry)
            db.session.commit()

            # SEND EMAIL ..............................................................................
            subject = f"Receipt-{session.get('receipt_no')}"
            reply_back_email = 'shwetabhartist@gmail.com'
            recipients_list = [data_dict['email']]
            body = f"Dear {data_dict['name'].split(' ')[0]}\n\nPlease find the receipt attached!"
            attachment_file_path = session.get('attachment_path')
            send_email_with_pdf_attachment(subject, reply_back_email, recipients_list, body, attachment_file_path)
            flash('Saved and Mailed successfully', 'success')
            return redirect(request.url)
            

        elif request.form.get('submit') == 'receipt-save-download':
            # Save PDF of the Receipt ...........................................................................
            png_path = session.get('file_directory')
            pdf_export_path = session.get('receipt_pdf_path')
            filename = png_to_pdf(png_path, pdf_export_path)[0]

            # Add Customer to MEMBER table database............................................................
            existing_uuid_list = []
            all_members = db.session.query(Member).all()
            for m in all_members:
                existing_uuid_list.append(m.uuid)

            uuid = create_uuid(existing_uuid_list, 6)
            data_dict = session.get('inv_receipt_data_dict')
            if db.session.query(Member).filter_by(email=data_dict['email']).scalar():
                pass
            else:
                entry = Member(
                    uuid = uuid,
                    email=data_dict['email'],
                    name=data_dict['name'],
                    phone=data_dict['phone'],
                    billing_address=data_dict['billing_address'],
                    billing_state=data_dict['billing_state'],
                    billing_country=data_dict['billing_country'],
                    billing_pincode=data_dict['billing_pincode'],
                    shipping_address=data_dict['shipping_address'],
                    shipping_state=data_dict['shipping_state'],
                    shipping_country=data_dict['shipping_country'],
                    shipping_pincode=data_dict['shipping_pincode'],
                    registration_date = str(date.today()),
                )
                db.session.add(entry)
                db.session.commit()

            # Add Receipt details to database..................................................................
            item_dict = data_dict['item_dict']
            items_name = ''
            items_price = ''
            items_quantity = ''

            for i in item_dict:
                if items_name == '':
                    items_name = item_dict[i]['item_description']
                else:
                    items_name = f"{items_name}%{item_dict[i]['item_description']}"
                if items_price == '':
                    items_price = item_dict[i]['price']
                else:
                    items_price = f"{items_price}%{item_dict[i]['price']}"
                if items_quantity == "":
                    items_quantity = item_dict[i]['qty']
                else:
                    items_quantity = f"{items_quantity}%{item_dict[i]['qty']}"
            date_time = datetime.now().replace(microsecond=0)
            member_id = db.session.query(Member).filter_by(email=data_dict['email']).scalar().id

            entry = Receipt(
                receipt_no=session.get('receipt_no'),
                name=data_dict['name'],
                billing_address=data_dict['billing_address'],
                billing_state=data_dict['billing_state'],
                billing_country=data_dict['billing_country'],
                billing_pincode=data_dict['billing_pincode'],
                shipping_address=data_dict['shipping_address'],
                shipping_state=data_dict['shipping_state'],
                shipping_country=data_dict['shipping_country'],
                shipping_pincode=data_dict['shipping_pincode'],
                phone=data_dict['phone'],
                email=data_dict['email'],
                items_name=items_name,
                items_price=items_price,
                items_quantity=items_quantity,
                tax_percent=data_dict['tax_percentage'],
                sub_total=session.get('sub_total'),
                grand_total=session.get('grand_total'),
                payment_type=data_dict['payment_type'],
                amount_paid=data_dict['partial_payment_amount_paid'],
                invoice_no=data_dict['receipt_invoice_no'],
                date_time = date_time,
                member_id=member_id
            )
            db.session.add(entry)
            db.session.commit()

            # DOWNLOAD ................................................................................
            receipt_file_path = pdf_export_path + filename + '.pdf'
            return send_file(
                receipt_file_path,
                as_attachment=True,         # True forces a browser download prompt
                download_name=f"{filename}.pdf"  # Sets the default name for the downloaded file
            )
        elif request.form.get('submit') == 'receipt-save-email-download':
            # Save PDF of the Receipt ...........................................................................
            png_path = session.get('file_directory')
            pdf_export_path = session.get('receipt_pdf_path')
            filename = png_to_pdf(png_path, pdf_export_path)[0]

            # Add Customer to MEMBER table database............................................................
            existing_uuid_list = []
            all_members = db.session.query(Member).all()
            for m in all_members:
                existing_uuid_list.append(m.uuid)

            uuid = create_uuid(existing_uuid_list, 6)
            data_dict = session.get('inv_receipt_data_dict')
            if db.session.query(Member).filter_by(email=data_dict['email']).scalar():
                pass
            else:
                entry = Member(
                    uuid = uuid,
                    email=data_dict['email'],
                    name=data_dict['name'],
                    phone=data_dict['phone'],
                    billing_address=data_dict['billing_address'],
                    billing_state=data_dict['billing_state'],
                    billing_country=data_dict['billing_country'],
                    billing_pincode=data_dict['billing_pincode'],
                    shipping_address=data_dict['shipping_address'],
                    shipping_state=data_dict['shipping_state'],
                    shipping_country=data_dict['shipping_country'],
                    shipping_pincode=data_dict['shipping_pincode'],
                    registration_date = str(date.today()),
                )
                db.session.add(entry)
                db.session.commit()

            # Add Receipt details to database..................................................................
            item_dict = data_dict['item_dict']
            items_name = ''
            items_price = ''
            items_quantity = ''

            for i in item_dict:
                if items_name == '':
                    items_name = item_dict[i]['item_description']
                else:
                    items_name = f"{items_name}%{item_dict[i]['item_description']}"
                if items_price == '':
                    items_price = item_dict[i]['price']
                else:
                    items_price = f"{items_price}%{item_dict[i]['price']}"
                if items_quantity == "":
                    items_quantity = item_dict[i]['qty']
                else:
                    items_quantity = f"{items_quantity}%{item_dict[i]['qty']}"
            date_time = datetime.now().replace(microsecond=0)
            member_id = db.session.query(Member).filter_by(email=data_dict['email']).scalar().id

            entry = Receipt(
                receipt_no=session.get('receipt_no'),
                name=data_dict['name'],
                billing_address=data_dict['billing_address'],
                billing_state=data_dict['billing_state'],
                billing_country=data_dict['billing_country'],
                billing_pincode=data_dict['billing_pincode'],
                shipping_address=data_dict['shipping_address'],
                shipping_state=data_dict['shipping_state'],
                shipping_country=data_dict['shipping_country'],
                shipping_pincode=data_dict['shipping_pincode'],
                phone=data_dict['phone'],
                email=data_dict['email'],
                items_name=items_name,
                items_price=items_price,
                items_quantity=items_quantity,
                tax_percent=data_dict['tax_percentage'],
                sub_total=session.get('sub_total'),
                grand_total=session.get('grand_total'),
                payment_type=data_dict['payment_type'],
                amount_paid=data_dict['partial_payment_amount_paid'],
                invoice_no=data_dict['receipt_invoice_no'],
                date_time = date_time,
                member_id=member_id
            )
            db.session.add(entry)
            db.session.commit()

            # SEND EMAIL ..............................................................................
            subject = f"Receipt-{session.get('receipt_no')}"
            reply_back_email = 'shwetabhartist@gmail.com'
            recipients_list = [data_dict['email']]
            body = f"Dear {data_dict['name'].split(' ')[0]}\n\nPlease find the receipt attached!"
            attachment_file_path = session.get('attachment_path')
            send_email_with_pdf_attachment(subject, reply_back_email, recipients_list, body, attachment_file_path)
            flash('Saved and Mailed successfully', 'success')

            # DOWNLOAD ................................................................................
            receipt_file_path = pdf_export_path + filename + '.pdf'
            return send_file(
                receipt_file_path,
                as_attachment=True,         # True forces a browser download prompt
                download_name=f"{filename}.pdf"  # Sets the default name for the downloaded file
            )
            
        if request.form.get('submit') == 'create-coa':
            file = request.files.get('artwork-img')
            s_no = request.form.get('serial_no')
            title = request.form.get('title')
            size = request.form.get('size')
            medium = request.form.get('medium')
            year = request.form.get('year')
            client_name = request.form.get('client_name')
            client_email = request.form.get('client_email')
            varnished = request.form.get('varnished')
            signed = request.form.get('signed')
            statement = request.form.get('statement')
            copyright_type = request.form.get('copyright')

            if file:
                filename = secure_filename(file.filename)
            
            temp_artwork_img_folder = f"./static/files/users/{current_user.uuid}/temp/artwork/"
            if not os.path.exists(temp_artwork_img_folder):
                os.makedirs(temp_artwork_img_folder)
            dir_path = Path(temp_artwork_img_folder)
            files = [str(f) for f in dir_path.iterdir() if f.is_file()]
            if len(files) > 0:
                for f in files:
                    os.remove(f)
            artwork_path = f"{temp_artwork_img_folder}{filename}"
            file.save(artwork_path)

            prepare_coa_result = prepare_coa(title, current_user.name, size, medium, varnished, year, signed, s_no, statement, copyright_type, artwork_path, current_user.uuid)[0]
            temp_coa_img_path = prepare_coa_result[0]
            date_today = prepare_coa_result[1]

            session['s_no'] = s_no
            session['title'] = title
            session['size'] = size
            session['medium'] = medium
            session['year'] = year
            session['client_name'] = client_name
            session['client_email'] = client_email
            session['varnished'] = varnished
            session['signed'] = signed
            session['statement'] = statement
            session['copyright_type'] = copyright_type
            session['coa_img_path'] = str(Path(temp_coa_img_path).parent)
            session['date_today'] = date_today
            
            return render_template('document_preview.html', preview_path='.'+temp_coa_img_path, current_year=current_year, admin=admin, logged_in=current_user.is_authenticated, document='COA')
        
        if request.form.get('submit') == 'coa-save-email':
            # -------------------------------- ADD TO DATABASE----------------------------------------------------------------- #
            s_no = session.get('s_no')
            title = session.get('title')
            size = session.get('size')
            medium = session.get('medium')
            year = session.get('year')
            client_name = session.get('client_name')
            client_email = session.get('client_email')
            varnished = session.get('varnished')
            signed = session.get('signed')
            statement = session.get('statement')
            copyright_type = session.get('copyright_type')
            coa_img_path = session.get('coa_img_path')
            date_today = session.get('date_today')
            export_path = f"./static/files/users/{current_user.uuid}/documents/coa/"

            coa_pdf_path = png_to_pdf(coa_img_path, export_path)[1]
    
            if client_email:
                client = db.session.query(Member).filter_by(email=client_email).scalar()
                client_id = client.id
            else:
                client_id = ''

            entry = Coa(
                serial_no=s_no,
                title=title,
                artist_name=current_user.name,
                size=size,
                medium=medium,
                varnished=varnished,
                year=year,
                signed=signed,
                statement=statement,
                copyright=copyright_type,
                client_name=client_name,
                artist_id=current_user.id,
                client_id=client_id
            )
            db.session.add(entry)
            db.session.commit()

            # ------------------------------- Email --------------------------------------------- #
            if client_email:
                subject = f"Certificate of Authenticity - Artwork_{s_no}"
                body = f"Dear {client_name}\n\nPlease find the Certificate of Authenticity for the artwork attached in the attachment."
                send_email_with_pdf_attachment(subject, 'shwetabhartist@gmail.com', [client_email], body, coa_pdf_path)

        elif request.form.get('submit') == 'coa-save-download':
            # -------------------------------- ADD TO DATABASE----------------------------------------------------------------- #
            s_no = session.get('s_no')
            title = session.get('title')
            size = session.get('size')
            medium = session.get('medium')
            year = session.get('year')
            client_name = session.get('client_name')
            client_email = session.get('client_email')
            varnished = session.get('varnished')
            signed = session.get('signed')
            statement = session.get('statement')
            copyright_type = session.get('copyright_type')
            coa_img_path = session.get('coa_img_path')
            export_path = f"./static/files/users/{current_user.uuid}/documents/coa/"

            coa_pdf_path = png_to_pdf(coa_img_path, export_path)[1]
    
            if client_email:
                client = db.session.query(Member).filter_by(email=client_email).scalar()
                client_id = client.id
            else:
                client_id = None

            entry = Coa(
                serial_no=s_no,
                title=title,
                artist_name=current_user.name,
                size=size,
                medium=medium,
                varnished=varnished,
                year=year,
                signed=signed,
                statement=statement,
                copyright=copyright_type,
                client_name=client_name,
                artist_id=current_user.id,
                client_id=client_id
            )
            db.session.add(entry)
            db.session.commit()

            # ------------------------------------- DOWNLOAD ------------------------------------------- #
            filename = Path(coa_pdf_path).name
            return send_file(
                coa_pdf_path,
                as_attachment=True,         # True forces a browser download prompt
                download_name=f"{filename}"  # Sets the default name for the downloaded file
            )

        elif request.form.get('submit') == 'coa-save-email-download':
            # -------------------------------- ADD TO DATABASE----------------------------------------------------------------- #
            s_no = session.get('s_no')
            title = session.get('title')
            size = session.get('size')
            medium = session.get('medium')
            year = session.get('year')
            client_name = session.get('client_name')
            client_email = session.get('client_email')
            varnished = session.get('varnished')
            signed = session.get('signed')
            statement = session.get('statement')
            copyright_type = session.get('copyright_type')
            coa_img_path = session.get('coa_img_path')
            export_path = f"./static/files/users/{current_user.uuid}/documents/coa/"

            coa_pdf_path = png_to_pdf(coa_img_path, export_path)[1]
    
            if client_email:
                client = db.session.query(Member).filter_by(email=client_email).scalar()
                client_id = client.id
            else:
                client_id = ''

            entry = Coa(
                serial_no=s_no,
                title=title,
                artist_name=current_user.name,
                size=size,
                medium=medium,
                varnished=varnished,
                year=year,
                signed=signed,
                statement=statement,
                copyright=copyright_type,
                client_name=client_name,
                artist_id=current_user.id,
                client_id=client_id
            )
            db.session.add(entry)
            db.session.commit()

            # ------------------------------- Email --------------------------------------------- #
            if client_email:
                subject = f"Certificate of Authenticity - Artwork_{s_no}"
                body = f"Dear {client_name}\n\nPlease find the Certificate of Authenticity for the artwork attached in the attachment."
                send_email_with_pdf_attachment(subject, 'shwetabhartist@gmail.com', [client_email], body, coa_pdf_path)

             # ------------------------------------- DOWNLOAD ------------------------------------------- #
            filename = Path(coa_pdf_path).name
            return send_file(
                coa_pdf_path,
                as_attachment=True,         # True forces a browser download prompt
                download_name=f"{filename}"  # Sets the default name for the downloaded file
            )


    if current_user.is_authenticated:
        if artist in current_user.role:
            return render_template('artist_dashboard.html', logged_in=current_user.is_authenticated, current_year=current_year, admin=admin)
        else:
            return redirect(url_for('main.home'))
    else:
        return redirect(url_for('main.home'))


@account.route('/instructor-dashboard', methods=['GET', 'POST'])
def instructor_dashboard():
    admin = db.session.query(Role).filter_by(name='admin').scalar()
    instructor = db.session.query(Role).filter_by(name='instructor').scalar()
    date_time = datetime.now().replace(microsecond=0)

    course_dict = {}
    courses = db.session.query(Workshop).all()
    for c in courses: 
        course_month_list = []

        course_uuid = c.uuid
        course_topic = c.topic
        course_months = c.months
        for m in course_months:
            course_month_list.append(m.month)
        course_dict[course_uuid] = {"course_uuid": course_uuid, "course_topic": course_topic, "months":course_month_list}

    
    
    if request.method == 'POST':
        if request.form.get('submit') == 'add-course-video':
            course_uuid = request.form.get('course-uuid')
            if course_uuid != 'default':
                title = request.form.get('lesson-title')
                video_yt_url = request.form.get('lesson-url')
                month = request.form.get('month')
                detail = request.form.get('lesson-detail')
                course_month_list = db.session.query(Workshop).filter_by(uuid=course_uuid).scalar().months
                for m in course_month_list:
                    if m.month == int(month):
                        course_month = m
                entry = MonthVideos(
                    title=title,
                    vid_id=video_yt_url,
                    detail=detail,
                    date_time=date_time,
                    month_id=course_month.id
                )
                try:
                    db.session.add(entry)
                    db.session.commit()
                    print('committed')
                    flash('Data added successfully, Chief!', 'success')
                except Exception as e:
                    flash('Failed to add, chief!', 'error')
                return redirect(url_for('account.instructor_dashboard'))
            else:
                flash('Aborted! Please select the Course/Workshop first!', 'error')
            
        if request.form.get('submit') == 'add-course-notes':
            course_uuid = request.form.get('course-uuid')
            if course_uuid != 'default':
                month = request.form.get('month')
                course_month_list = db.session.query(Workshop).filter_by(uuid=course_uuid).scalar().months
                for m in course_month_list:
                    if m.month == int(month):
                        course_month = m
                if 'file' not in request.files:
                    flash('No file part', 'error')
                    return redirect(request.url)
                files = request.files.getlist('file')
                notes_pdf_output_name = request.form.get('note_file_name')
                if '.pdf' not in notes_pdf_output_name:
                    notes_pdf_output_name = str(notes_pdf_output_name) + '.pdf'
                
                folder_name = course_uuid
                folder = f"./static/files/courses/{folder_name}/{month}/notes/"
                if not os.path.exists(folder):
                    os.makedirs(folder)
                existing_notes_uuid = []
                existing_notes = db.session.query(MonthNotes).all()
                for n in existing_notes:
                    existing_notes_uuid.append(n.uuid)

                uuid = create_uuid(existing_notes_uuid, 4)
                existing_notes_uuid.append(uuid)
                filename = str(uuid) + str('$') + str(notes_pdf_output_name)
                multiple_images_to_pdf(filestorage_list=files, image_directory='', output_pdf_directory=folder, output_pdf_file_name=filename, quality=50)
                
                date_time = datetime.now().replace(microsecond=0)
                
                entry = MonthNotes(
                    uuid=uuid,
                    file_name=filename,
                    month_id=course_month.id,
                    date_time=date_time
                )
                db.session.add(entry)
                db.session.commit()
                flash('Chief! Files uploaded successfully!', 'success')

        if request.form.get('submit') == 'add-course-assignments':
            if 'assignments' not in request.files:
                flash('No file part', 'error')
                return redirect(request.url)
            files = request.files.getlist('assignments')
            assignment_pdf_output_name = request.form.get('assignment_file_name')
            if '.pdf' not in assignment_pdf_output_name:
                assignment_pdf_output_name = str(assignment_pdf_output_name) + '.pdf'

            course_uuid = request.form.get('course-uuid')
            if course_uuid != 'default':
                month = request.form.get('month')
                course_month_list = db.session.query(Workshop).filter_by(uuid=course_uuid).scalar().months
                for m in course_month_list:
                    if m.month == int(month):
                        course_month = m
                folder_name = course_uuid
                if folder_name != 'default':
                    folder = f"./static/files/courses/{folder_name}/{month}/assignments/"
                    if not os.path.exists(folder):
                        os.makedirs(folder)
                    existing_assignments_uuid = []
                    existing_assignments = db.session.query(MonthAssignments).all()
                    for a in existing_assignments:
                        existing_assignments_uuid.append(a.uuid)

                    uuid = create_uuid(existing_assignments_uuid, 4)
                    filename = str(uuid) + str("$") + str(assignment_pdf_output_name)
                    multiple_images_to_pdf(filestorage_list=files, image_directory='', output_pdf_directory=folder, output_pdf_file_name=filename, quality=50)

                    date_time = datetime.now().replace(microsecond=0)

                    entry = MonthAssignments(
                        uuid=uuid,
                        file_name=filename,
                        month_id=course_month.id,
                        date_time=date_time
                    )
                    db.session.add(entry)
                    db.session.commit()
                    flash('Chief! Files uploaded successfully!', 'success')
                    return redirect(request.url)
                else:
                    flash('Aborted! Please select the Course/Workshop first!', 'error')

        if request.form.get('submit') == 'add-course-demo':
            course_uuid = request.form.get('course-uuid')
            if course_uuid != 'default':
                demo_title = request.form.get('demo-title')
                demo_yt_url = request.form.get('demo-url')
                month = request.form.get('month')
                course_month_list = db.session.query(Workshop).filter_by(uuid=course_uuid).scalar().months
                for m in course_month_list:
                    if m.month == int(month):
                        course_month = m
                date_time = datetime.now().replace(microsecond=0)
                try:
                    entry = MonthDemo(
                        month_id=course_month.id,
                        yt_vid_id=demo_yt_url,
                        vid_caption=demo_title,
                        instructor='Shwetabh Suman',
                        date_time=date_time
                    )
                    db.session.add(entry)
                    db.session.commit()
                    flash("Demo video added successfully", "success")
                except Exception as e:
                    p(e)
                    flash("Couldn't add Demo video", 'error')
                    
        if request.form.get('submit') == 'add-assessed-video':
            course_uuid = request.form.get('course-uuid')
            if course_uuid != 'default':
                yt_vid_id = request.form.get('assessed-vid-id')
                vid_caption = request.form.get('assessed-vid-caption')
                teacher = 'Shwetabh Suman'
                date_time = datetime.now().replace(microsecond=0)
                month = request.form.get('month')
                course_month_list = db.session.query(Workshop).filter_by(uuid=course_uuid).scalar().months
                for m in course_month_list:
                    if m.month == int(month):
                        course_month = m
                entry = MonthAssignmentAssessmentVideos(
                    month_id= course_month.id,
                    yt_vid_id=yt_vid_id,
                    vid_caption=vid_caption,
                    instructor=teacher,
                    date_time=date_time
                )

                db.session.add(entry)
                db.session.commit()
                flash('Assessment video ID successfully uploaded!', 'success')
            else:
                flash('Please select the course first!', 'error')
        
        if request.form.get('submit') == 'enrolment-alert':
            current_status = request.form.get('current-status')
            if current_status == 'on':
                db.session.query(Tools).filter_by(keyword='show_next_month_enrolment_alert').scalar().data = 'off'
            else:
                db.session.query(Tools).filter_by(keyword='show_next_month_enrolment_alert').scalar().data = 'on'
            db.session.commit()
            flash('Successfully changes the next month enrolment alert status', 'success')

        if request.form.get('submit') == 'set-current-course-month':
            course_uuid = request.form.get('course-uuid')
            month = request.form.get('month')
            db.session.query(Tools).filter_by(keyword="current_course_uuid").scalar().data = course_uuid
            db.session.query(Tools).filter_by(keyword="current_course_month").scalar().data = month
            db.session.commit()
            flash('Current course and month successfully updated', 'success')

        if request.form.get('submit') == 'set-monthly-fee':
            course_uuid = request.form.get('course-uuid')
            month = request.form.get('month')
            fee = request.form.get('fee')
            db.session.query(Tools).filter_by(keyword='current_course_monthly_fee').scalar().data = fee
            db.session.commit()
            flash('Current course monthly fee successfully updated', 'success')

        if request.form.get('submit') == 'new-course':
            topic = request.form.get('topic')
            category = request.form.get('category')
            course_uuid_list = []
            for data in db.session.query(Workshop).all():
                course_uuid_list.append(data.uuid)
            course_uuid = create_uuid(course_uuid_list, 6)
            entry = Workshop(
                uuid=course_uuid,
                topic=topic,
                instructor='Shwetabh Suman'
            )
            db.session.add(entry)
            db.session.commit()
            course_id = db.session.query(Workshop).filter_by(uuid=course_uuid).scalar().id
            entry2 = WorkshopDetails(
                category=category,
                ws_id=course_id
            )
            db.session.add(entry2)
            db.session.commit()
            flash('Course created!', 'success')

        if request.form.get('submit') == 'workshop-month':
            if request.form.get('course-uuid') != 'default':
                month_count = request.form.get('month-count')
                course_uuid = request.form.get('course-uuid')
                course = db.session.query(Workshop).filter_by(uuid=course_uuid).scalar()
                month_uuid_list = []
                for data in db.session.query(WorkshopMonth).all():
                    month_uuid_list.append(data.uuid)
                for i in range(int(month_count)):
                    month_uuid = create_uuid(month_uuid_list, 4)
                    month_uuid_list.append(month_uuid)
                    month_name = i+1
                    entry = WorkshopMonth(
                        uuid = month_uuid,
                        month = month_name,
                        title = '',
                        detail = '',
                        workshop_id = course.id
                    )
                    db.session.add(entry)
                    db.session.commit()
                    flash('Months added', 'success')

        if request.form.get('submit') == 'assignment_details':
            if request.form.get('course_uuid') != 'default':
                course_uuid = request.form.get('course_uuid')
                return redirect(url_for('account.instructor_dashboard_canvas', course_uuid=course_uuid, action='assignment_details'))
                
        if request.form.get('submit') == 'download-assignments':
            course_uuid = request.form.get('course_uuid')
            if course_uuid != 'default':
                folder = f"./static/files/courses/{course_uuid}/assignment-submissions"
                dest_folder = f"./static/files/courses/{course_uuid}/assignment-submissions/assessed/"
                file_lists = []

    # 2. Create an in-memory byte stream --------------------------------------------
                memory_file = BytesIO()

    # 3. Write files into the ZIP archive --------------------------------------------
                exclude_names = {'assessed'}
                with ZipFile(memory_file, 'w', ZIP_DEFLATED) as zf:
                    for root, dirs, files in os.walk(folder):
                        dirs[:] = [d for d in dirs if d not in exclude_names]
                        for file in files:
                            file_path = os.path.join(root, file)
                            file_lists.append(file_path)
                            archive_name = os.path.relpath(file_path, folder)
                            zf.write(file_path, archive_name)
                
    # 4. Reset the file pointer to the beginning of the stream ---------------------------
                memory_file.seek(0)

                move_files(file_lists, dest_folder)
    # 5. Return the stream as a downloadable attachment -----------------------------------
                return send_file(
                    memory_file,
                    mimetype='application/zip',
                    as_attachment=True,
                    download_name=f"{course_uuid}_{course_topic}_assignments.zip"
                )
            else:
                flash('Please select the Course first!', 'error')

    if current_user.is_authenticated:
        if instructor in current_user.role:
            next_month_enrolment_alert_status = db.session.query(Tools).filter_by(keyword="show_next_month_enrolment_alert").scalar().data

            return render_template('instructor-dashboard.html', logged_in=current_user.is_authenticated, current_year=current_year,
                           admin=admin, course_dict=course_dict, next_month_enrolment_alert_status=next_month_enrolment_alert_status)
    else:
        return redirect(url_for('main.home'))


@account.route('/instructor_dashboard_canvas', methods=['GET', 'POST'])
def instructor_dashboard_canvas():
    pending_assignments_count = 0
    assessed_assignments_count = 0
    student_assignment_dict = {}

    admin = db.session.query(Role).filter_by(name='admin').scalar()
    course_uuid = request.args.get('course_uuid')
    action = request.args.get('action')
    if action == 'assignment_details':
        course_title = db.session.query(Workshop).filter_by(uuid=course_uuid).scalar().topic
        pending_assignments_folder = Path(f'./static/files/courses/{course_uuid}/assignment-submissions/')
        assessed_assignments_folder = Path(f'./static/files/courses/{course_uuid}/assignment-submissions/assessed/')
        if not os.path.exists(pending_assignments_folder):
            os.makedirs(pending_assignments_folder)
        if not os.path.exists(assessed_assignments_folder):
            os.makedirs(assessed_assignments_folder)
        pending_assignments_count = sum(1 for item in pending_assignments_folder.iterdir() if item.is_file())
        assessed_assignments_count = sum(1 for item in assessed_assignments_folder.iterdir() if item.is_file())
        total_assignment_count = pending_assignments_count + assessed_assignments_count

        pending_assignments_list = [f.name for f in pending_assignments_folder.iterdir() if f.is_file()]
        assessed_assignments_list = [f.name for f in assessed_assignments_folder.iterdir() if f.is_file()]
        all_students_enrolled = db.session.query(Workshop).filter_by(uuid=course_uuid).scalar().participants
        total_pending = 0
        total_assessed = 0
        for s in all_students_enrolled:
            name = s.name
            uuid = s.uuid
            for f in assessed_assignments_list:
                if f.split('_')[1] == str(uuid):
                    p(f.split('_')[1])
                    p(uuid)
                    total_assessed += 1
            for f in pending_assignments_list:
                if f.split('_')[1] == str(uuid):
                    p('Found')
                    total_pending += 1
            total = total_pending + total_assessed
            student_assignment_dict[name] = {
                'pending': total_pending,
                'assessed': total_assessed,
                'total': total
            }
            total_pending = 0
            total_assessed = 0

        return render_template('instructor_dashboard_canvas.html', pending_assignments_count=pending_assignments_count, assessed_assignments_count=assessed_assignments_count, total_assignment_count=total_assignment_count,
                                        logged_in=current_user.is_authenticated, current_year=current_year, title=course_title, action=action, admin=admin, student_assignment_dict=student_assignment_dict)
    return render_template('account.instructor_dashboard_canvas.html', logged_in=current_user.is_authenticated, current_year=current_year, admin=admin)

@account.route('/contact-instructor', methods=['GET', 'POST'])
def contact_instructor():
    if not current_user.is_authenticated:
        return redirect(url_for('account.login'))

    if request.method == 'POST':
        if request.form.get('submit') == 'instructor-contact':
            name = request.form.get('name')
            phone = request.form.get('contact')
            email = request.form.get('email')
            user_id = request.form.get('user_id')
            message = request.form.get('message')

            subject = 'Student Message- URGENT!'
            message_body = f'New School Message:\n\nName: {name}\nEmail: {email}\n' \
                           f'Phone: {phone}' \
                           f'\nUser_id: {user_id}\n\nMessage: {message}\n\n'
            send_email_with_reply(subject, email, ['shwetabhartist@gmail.com'], message_body)

            flash('Message sent successfully', 'success')

    return render_template('contact_instructor.html', logged_in=current_user.is_authenticated, current_year=current_year)


@account.route('/edit-account-info', methods=['GET', 'POST'])
def edit_account_info():
    admin = db.session.query(Role).filter_by(name='admin').scalar()

    if request.method == 'POST':
        if request.form.get('submit') == 'edit-name':
            name = request.form.get('name')
            current_user.name = name
            try:
                db.session.commit()
                flash('Name changed successfully!', 'success')
            except Exception as e:
                flash('Name failed to change!', 'error')
        if request.form.get('submit') == 'edit-email':
            email = request.form.get('email')
            current_user.email = email
            try:
                db.session.commit()
                flash('Email changed successfully!', 'success')
            except Exception as e:
                flash('Email failed to change!', 'error')
        if request.form.get('submit') == 'edit-phone':
            phone = request.form.get('phone')
            current_user.phone = phone
            try:
                db.session.commit()
                flash('Phone changed successfully!', 'success')
            except Exception as e:
                flash('Phone failed to change!', 'error')
        if request.form.get('submit') == 'edit-whatsapp':
            whatsapp = request.form.get('whatsapp')
            current_user.whatsapp = whatsapp
            try:
                db.session.commit()
                flash('Whatsapp changed successfully!', 'success')
            except Exception as e:
                flash('Whatsapp failed to change!', 'error')
        if request.form.get('submit') == 'edit-profession':
            profession = request.form.get('profession')
            current_user.profession = profession
            try:
                db.session.commit()
                flash('Profession changed successfully!', 'success')
            except Exception as e:
                flash('Profession failed to change!', 'error')
        if request.form.get('submit') == 'edit-state':
            state = request.form.get('state')
            current_user.state = state
            try:
                db.session.commit()
                flash('State changed successfully!', 'success')
            except Exception as e:
                flash('State failed to change!', 'error')
        if request.form.get('submit') == 'edit-facebook':
            facebook = request.form.get('facebook')
            current_user.fb_url = facebook
            try:
                db.session.commit()
                flash('Facebook changed successfully!', 'success')
            except Exception as e:
                flash('Facebook failed to change!', 'error')
        if request.form.get('submit') == 'edit-instagram':
            instagram = request.form.get('instagram')
            current_user.insta_url = instagram
            try:
                db.session.commit()
                flash('Instagram changed successfully!', 'success')
            except Exception as e:
                flash('Instagram failed to change!', 'error')
        if request.form.get('submit') == 'edit-x':
            x = request.form.get('x')
            current_user.x = x
            try:
                db.session.commit()
                flash('X changed successfully!', 'success')
            except Exception as e:
                flash('X failed to change!', 'error')
        if request.form.get('submit') == 'edit-website':
            website = request.form.get('website')
            current_user.website = website
            try:
                db.session.commit()
                flash('Website changed successfully!', 'success')
            except Exception as e:
                flash('Website failed to change!', 'error')

    return render_template('edit_account_info.html', logged_in=current_user.is_authenticated, current_year=current_year,
                           admin=admin)


@account.route('/support', methods=['GET', 'POST'])
def support():
    ticket_category = db.session.query(Tools).filter_by(keyword='ticket_category').scalar().data
    issue_category_list = ticket_category.split('/')

    all_ticket_no_list = []
    all_ticket_no = db.session.query(SupportTicket).all()
    for t in all_ticket_no:
        all_ticket_no_list.append(t.ticket_no)

    if request.method == 'POST':
        if request.form.get('submit') == 'create-ticket':
            subject = request.form.get('problem-category')
            if subject != 'default':
                member_id = request.form.get('member_id')
                msg = request.form.get('message')
                continue_process = True
                while continue_process:
                    ticket_no = random.randint(100000, 999999)
                    if ticket_no not in all_ticket_no_list:
                        continue_process = False
            
            entry = SupportTicket(
                ticket_no=ticket_no,
                member_id=member_id,
                msg=msg,
                subject=subject,
                status='open'
            )
            try:
                db.session.add(entry)
                db.session.commit()
                flash('Your Issue got submitted successfully', 'success')
            except Exception as e:
                flash('Problem in submitting Issue!', 'error')

    return render_template('support.html', issue_category_list=issue_category_list, current_year=current_year, logged_in=current_user.is_authenticated)


@account.route('/registration_form', methods=['GET', 'POST'])
def registration_form():
    num_list = []
    uuid_list = []

    result = db.session.query(Member).all()
    for user in result:
        uuid_list.append(user.uuid)
        num = user.phone
        if len(num) == 10:
            user_no = f"91{num}"
        elif len(num) == 11 and num[0] == '0':
            user_no = f'91{num[1:]}'
        elif len(num) == 12 and num[:2] == '91':
            user_no = num
        elif len(num) == 13:
            user_no = num[3:]
        else:
            user_no = num
        num_list.append(user_no)

    if request.method == 'POST':
        if request.form.get('submit') == 'proceed':
            ph = request.form.get('phone')
            if len(ph) == 10:
                phone = f"91{ph}"
            elif len(ph) == 11 and ph[0] == '0':
                phone = f'91{ph[1:]}'
            elif len(ph) == 12 and ph[:2] == '91':
                phone = ph
            elif len(ph) == 13:
                phone = ph[3:]
            else:
                phone = ph

            email = request.form.get('email')
            state = request.form.get('state')
            result = db.session.execute(db.select(Member).where(Member.email == email))
            user = result.scalar()
            if user:
                flash("You've already signed up with that email, log in instead!", "error")
                return redirect(url_for('account.login'))
            if phone in num_list:
                flash("Already an account exists with phone number. Please register with different phone number or log in",
                    "error")
                return redirect(url_for('account.register'))
            hash_and_salted_password = generate_password_hash(
                request.form.get('password'),
                method='pbkdf2:sha256',
                salt_length=8
            )
            date_ = request.form.get('date')
            if len(date_) < 2:
                date_ = "0" + date_
            month = request.form.get('month')
            if len(month) < 2:
                month = "0" + month
            year = request.form.get('year')
            dob = f"{year}-{month}-{date_}"
            age = calculate_age(dob)

            artist_account = request.form.get('artist_account')

            # if age < 13:
            #     flash("You're below 13 year. Really very sorry we cannot take you in!", "error")
            #     return redirect(request.url)

            unique = False
            uuid = ''
            while not unique:
                u = random.randint(100000, 999999)
                if u not in uuid_list:
                    uuid = u
                    unique = True

        # ------------------------------------------ Add details to session ----------------------------------------- #
            session['name'] = request.form.get('name')
            session['email'] = request.form.get('email')
            session['password'] = hash_and_salted_password
            session['phone'] = request.form.get('phone')
            session['whatsapp'] = request.form.get('whatsapp')
            session['sex'] = request.form.get('sex')
            session['dob'] = dob
            session['profession'] = request.form.get('profession')
            session['state'] = state
            session['uuid'] = uuid
            return redirect(url_for('account.captcha_verification'))

    return render_template("register.html", logged_in=current_user.is_authenticated, current_year=current_year)



@account.route('/captcha-verification', methods=['GET', 'POST'])
def captcha_verification():
    captcha_value, captcha_uri = generate_captcha()
    session['captcha_value'] = captcha_value
    return render_template("captcha_verification.html", current_year=current_year, captcha=captcha_uri)



@account.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        if request.form.get('submit') == 'register':
            captcha = request.form.get('captcha')
            captcha_value = session['captcha_value']
            if captcha == captcha_value:
                name = session['name']
                email = session['email']
                password = session['password']
                phone = session['phone']
                whatsapp = session['whatsapp']
                sex = session['sex']
                dob = session['dob']
                profession = session['profession']
                state = session['state']
                uuid = session['uuid']

                new_user = Member(
                    email=email,
                    password=password,
                    name=name,
                    phone=phone,
                    whatsapp=whatsapp,
                    profession=profession,
                    sex=sex,
                    dob=dob,
                    state=state,
                    registration_date=today_date,
                    uuid=uuid
                )
                db.session.add(new_user)
                db.session.commit()

                all_users = db.session.query(Member)
                admin = db.session.query(Role).filter_by(name='admin').scalar()

                if len(all_users.all()) == 1:
                    all_users[0].role.append(admin)
                    db.session.commit()

                login_user(new_user)
                session['logged_in'] = True

                # if artist_account == 'yes':
                #     artist = db.session.query(Role).filter_by(name='artist').one()
                #
                #     current_user.role.append(artist)
                #     db.session.commit()
                #     entry = ArtistData(
                #         artist=current_user.name,
                #         watermarked_artworks=0,
                #         gallery_artworks=0,
                #         all_collections=0,
                #         commission_collections=0,
                #         sold_artworks=0,
                #         queried_artworks=0,
                #         shipped_artworks=0,
                #         contracted_artworks=0,
                #         sold_commissions=0,
                #         memory_occupied_total=0,
                #         memory_occupied_gallery=0,
                #         member=current_user,
                #     )
                #     db.session.add(entry)
                #     db.session.commit()

                mail = render_template('mails/registration_success.html')
                send_email_support('Registration success!', [email],
                                '',
                                mail, '')
                mail_message = f'New Registration:\n\nName: {name}\nEmail: {email}\n' \
                            f'Phone: {phone}\n' \
                            f'Sex: {sex}\nProfession: {profession}\n' \
                            f'State: {state}\n\n'
                send_email_support('New Registration!', ['writartstudios@gmail.com'], mail_message, '', '')
                if 'url' in session:
                    return redirect(session['url'])
                return redirect(url_for('account.home', name=current_user.name.split()[0]))
            else:
                flash("Aborted! Captcha doesn't match!", "error")
                
    return render_template("register.html", logged_in=current_user.is_authenticated, current_year=current_year)


@account.route('/login', methods=['GET', 'POST'])
def login():
    num_list = []
    raw_num_list = []
    result = db.session.query(Member)
    if request.args.get('instruction'):
        instruction = request.args.get('instruction')
    else:
        instruction = 'Login'
    for user in result:
        num = user.phone
        raw_num_list.append(num)
        if len(num) == 10:
            user_no = f"91{num}"
        elif len(num) == 11 and num[0] == '0' or '+':
            user_no = f'91{num[1:]}'
        elif len(num) == 12 and num[:2] == '91':
            user_no = num
        elif len(num) == 13 and num[:3] == '+91':
            user_no = num[3:]
        else:
            user_no = num
        num_list.append(user_no)
    if request.method == 'POST':
        if request.form.get('submit') == 'update_details':
            pwd = request.form.get('password2')
            retype_pwd = request.form.get('retype-password2')
            if pwd != retype_pwd:
                flash("Retyped password did not match! Please try again.", "error")
                return render_template('update_account.html')
            hash_and_salted_password = generate_password_hash(
                pwd,
                method='pbkdf2:sha256',
                salt_length=8
            )
            current_user.password = hash_and_salted_password
            current_user.sex = request.form.get('sex')
            date_ = request.form.get('date')
            if len(date_) < 2:
                date_ = "0" + date_
            month = request.form.get('month')
            if len(month) < 2:
                month = "0" + month
            year = request.form.get('year')
            current_user.dob = f"{year}-{month}-{date_}"
            current_user.profession = request.form.get('profession')
            current_user.state = request.form.get('state')
            db.session.commit()
            return redirect(url_for('account.home'))
        if request.form.get('submit') == 'login':
            data = request.form.get('email-phone')
            if '@' in data:
                email = data
                result = db.session.execute(db.select(Member).where(Member.email == email))
                user = result.scalar()
            else:
                user_phone = ''
                ph = data
                if len(ph) == 10:
                    phone = f"91{ph}"
                elif len(ph) == 11 and ph[0] == '0' or '+':
                    phone = f'91{ph[1:]}'
                elif len(ph) == 12 and ph[:2] == '91':
                    phone = ph
                elif len(ph) == 13 and ph[:3] == '+91':
                    phone = ph[3:]
                else:
                    phone = ph
                if phone in num_list:
                    index = num_list.index(phone)
                    user_phone = raw_num_list[index]
                result = db.session.execute(db.select(Member).where(Member.phone == user_phone))
                user = result.scalar()
            password = request.form.get('password')

            # Email or Phone doesn't exist or password incorrect:
            if not user:
                flash("That Email or Phone does not exist, please try again.", category="error")
            elif not check_password_hash(user.password, password):
                flash('Password incorrect, please try again.', category='error')
            else:
                login_user(user)
                student = db.session.query(Role).filter_by(name='student').scalar()
                admin = db.session.query(Role).filter_by(name='admin').scalar()
                instructor = db.session.query(Role).filter_by(name='instructor').scalar()
                artist = db.session.query(Role).filter_by(name='artist').scalar()
                user_roles = current_user.role
                session['logged_in'] = True
                if session.get('url') == url_for('school.classroom'):
                    return redirect(url_for('school.classroom'))
                if session.get('url') == url_for('school.enroll'):
                    return redirect(url_for('school.enroll'))
                if len(user_roles) > 1:
                    return redirect(url_for('account.main_dashboard'))
                else:
                    if student in user_roles:
                        return redirect(url_for('account.student_dashboard'))
                    if admin in user_roles:
                        return redirect(url_for('manager.home'))
                    if instructor in user_roles:
                        return redirect(url_for('account.instructor_dashboard'))
                    if artist in user_roles:
                        return redirect(url_for('account.artist_dashboard'))
                    if not current_user.sex or current_user.sex == '':
                        return render_template('update_account.html')
                    if request.form.get('prev-page') == 'enroll':
                        flash("You are successfully logged in. Now proceed to enroll", "success")
                        return redirect(url_for('payment.home'))
                    if request.form.get('prev-page') == 'change-password':
                        flash("You are successfully logged in. Now proceed to change password", "success")
                        return redirect(url_for('account.change_password'))
                    if 'url' in session:
                        return redirect(session['url'])
                    else:
                        return redirect(url_for('main.home'))
                # return redirect(url_for('account.home', name=current_user.name.split()[0]))

    return render_template("login.html", instruction=instruction, current_year=current_year)


@account.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    email_list = []

    if request.method == 'POST':
        if request.form.get('submit') == 'get-password-reset-email':
            results = db.session.query(Member)
            token = random.randint(1000, 9999)

            if '@' in request.form.get('email_phone'):
                email = request.form.get('email_phone')
                for result in results:
                    if email == result.email:
                        email_list.append(email)
                        result.token = token
                        db.session.commit()
                        current_date_time = datetime.now()
                        send_email_support(subject=f"Password reset- {current_date_time}",
                                           recipients=email_list, body='',
                                           html=render_template('mails/password_reset_link.html',
                                                                link=f"https://writart.com/account/set_new_password?token={str(token)}&email={email_list[0]}"),
                                           image_dict='')
                        return render_template('check_mail_notification.html')

                    else:
                        flash('No account found with the entered email!', 'error')

            else:
                phone = request.form.get('email_phone')
                if len(phone) == 11 and phone[0] == '0':
                    phone = phone[1:]
                elif phone[0] == '+':
                    phone = phone[1:]
                for result in results:
                    r_phone = result.phone
                    if len(r_phone) == 11 and r_phone[0] == '0':
                        r_phone = r_phone[1:]
                    elif r_phone[0] == '+':
                        r_phone = r_phone[1:]
                    if phone == r_phone:
                        email = result.email
                        email_list.append(email)
                        result.token = token
                        db.session.commit()
                        current_date_time = datetime.now()
                        send_email_support(subject=f"Password reset - {current_date_time}",
                                           recipients=email_list, body='',
                                           html=render_template('mails/password_reset_link.html',
                                                                link=f"https://writart.com/account/set_new_password?token={str(token)}&email={email_list[0]}"),
                                           image_dict='')
                        return render_template('check_mail_notification.html')
                    else:
                        flash("No account found with the entered phone", "error")

        if request.form.get('submit') == 'set-password':
            new_pwd = request.form.get('password')
            email = request.form.get('mail')
            hash_and_salted_password = generate_password_hash(
                new_pwd,
                method='pbkdf2:sha256',
                salt_length=8
            )
            user = db.session.query(Member).filter_by(email=email).scalar()
            user.password = hash_and_salted_password

            db.session.commit()
            login_user(user)
            flash('New password set successfully!', 'success')
            mail = render_template('mails/password_reset_notification.html')
            send_email_support('Password Reset', [email],
                               '',
                               mail, '')
            if 'url' in session:
                return redirect(session['url'])

            return redirect(url_for('account.home'))

    return render_template("forgot_password.html", current_year=current_year)


@account.route('/set_new_password', methods=['GET', 'POST'])
def set_new_password():
    entered_token = request.args.get('token')
    email = request.args.get('email')
    token = db.session.query(Member).filter_by(email=email).one().token
    if str(token) == str(entered_token):
        return render_template('set_new_password.html', email=email)
    else:
        flash("Some error occured!", "error")
        send_email_support('ERROR!!!', ['writartstudios@gmail.com', 'shwetabhartist@gmail.com'], f"Problem forget password reset for {email}, Tokens don't match!",
                           '', '')
        return redirect(url_for("account.login"))


@account.route('/logout')
@login_required
def logout():
    logout_user()
    session['logged_in'] = False
    if 'url' in session:
        return redirect(session['url'])
    return redirect(url_for('main.home'))


@account.route('/breach-report', methods=['GET','POST'])
def breach_report():
    if request.method == 'POST':
        message = request.form.get('message')
        email_phone = request.form.get('email_phone')
        if '@' in email_phone:
            body = f"Dear member,\nWe have received your breach report.\nRelax! We'll help in your account " \
                   f"recovery({email_phone}).\nWe will reach you soon to verify and recover your account!\n"
            send_email_support('Account Breach Report', [email_phone], body, '', '')
        else:
            pass
        mail_body = f"Dear Admin,\nWe received breach report for this account.\n\nAccount details:\nEmail or Phone: " \
                    f"{email_phone}\nMessage: {message}\n"
        send_email_support('Account Breach Report', ['writartstudios@gmail.com', 'writart11@gmail.com'], mail_body, '',
                           '')
        flash("Breach-report sent to admin successfully!", "success")
    return render_template('breach-report.html')


@account.route('/change-password', methods=['GET','POST'])
def change_password():
    session['url'] = url_for('account.change_password')
    if request.method == 'POST':
        old_pwd = request.form.get('old-pwd')
        if not check_password_hash(current_user.password, old_pwd):
            flash("Please enter the correct old password", category="error")
        else:
            hash_and_salted_password = generate_password_hash(
                request.form.get('new-pwd'),
                method='pbkdf2:sha256',
                salt_length=8
            )
            current_user.password = hash_and_salted_password
            db.session.commit()
            flash("Password changed successfully", category="success")
    if current_user.is_authenticated:
        return render_template('change-password.html', logged_in=current_user.is_authenticated)
    else:
        instruction = 'Please first login to change password'
        return render_template('account/login.html', prev_page='change-password', instruction=instruction)
