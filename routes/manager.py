import os
import pandas as pd
from flask import Blueprint, render_template, request, flash, redirect, url_for, send_file
from flask_login import login_required, current_user

from extensions import db
from messenger import send_email_school, send_wa_msg_by_list, send_email_school_and_wa_msg_by_list
from models.payment import Payment
from models.query import Query
from models.tool import Tools
from models.user import User, Workshop, Role
from models.workshop_details import WorkshopDetails
from routes.account import today_date

manager = Blueprint('manager', __name__, static_folder='static', template_folder='templates')


def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


@manager.route('/', methods=['GET', 'POST'])
@login_required
def home():
    current_workshop = current_ws = db.session.query(Workshop)[db.session.query(Workshop).count()-1]
    current_ws_name = current_workshop_name = current_workshop.name
    current_ws_topic = current_workshop_topic = current_workshop.topic
    if db.session.query(Role).filter(Role.name == 'admin').scalar() in current_user.role:
        if request.method == 'POST':
            if request.form.get('name'):
                name = request.form.get('name')
                topic = request.form.get('topic')
                dt = request.form.get('date')
                if len(dt) < 2:
                    dt = "0" + dt
                month = request.form.get('month')
                if len(month) < 2:
                    month = "0" + month
                year = request.form.get('year')
                date_ = f"{year}-{month}-{dt}"
                instructor_ = request.form.get('instructor')
                session_link = request.form.get('link')
                entry = Workshop(
                    name=name,
                    topic=topic,
                    date=date_,
                    instructor=instructor_,
                    joining_link=session_link,
                    reg_start=today_date,
                )
                db.session.add(entry)
                db.session.commit()
                flash('New Workshop Added', 'success')
                return redirect(url_for('manager.home'))

            if request.form.get('category'):
                entry = WorkshopDetails(
                    category=request.form.get('category'),
                    brief=request.form.get('brief'),
                    sessions=request.form.get('sessions'),
                    subtopic1=request.form.get('st1'),
                    subtopic2=request.form.get('st2'),
                    subtopic3=request.form.get('st3'),
                    subtopic4=request.form.get('st4'),
                    subtopic5=request.form.get('st5'),
                    subtopic6=request.form.get('st6'),
                    subtopic7=request.form.get('st7'),
                    subtopic8=request.form.get('st8'),
                    subtopic9=request.form.get('st9'),
                    description=request.form.get('description'),
                    req1=request.form.get('req1'),
                    req2=request.form.get('req2'),
                    req3=request.form.get('req3'),
                    req4=request.form.get('req4'),
                    req5=request.form.get('req5'),
                    req6=request.form.get('req6'),
                    req7=request.form.get('req7'),
                    req8=request.form.get('req8'),
                    req9=request.form.get('req9'),
                    result1=request.form.get('result1'),
                    result2=request.form.get('result2'),
                    result3=request.form.get('result3'),
                    result4=request.form.get('result4'),
                    result5=request.form.get('result5'),
                    result6=request.form.get('result6'),
                    result7=request.form.get('result7'),
                    result8=request.form.get('result8'),
                    result9=request.form.get('result9'),
                    cover=f"{models.workshop.current_ws_name()}/cover.jpg",
                    thumbnail=f"{current_ws_name}/thumbnail.jpg",
                    photo1=f'{current_ws_name}/p1',
                    photo2=f'{current_ws_name}/p2',
                    photo3=f'{current_ws_name}/p3',
                    workshop=current_ws,
                )
                try:
                    db.session.add(entry)
                    db.session.commit()
                    flash('Workshop details added successfully, Chief!', 'success')
                except:
                    flash("Sorry, Couldn't add, Chief!", "error")

            if request.form.get('session-link'):
                ws_count = db.session.query(Workshop).count()
                current_workshop = db.session.query(Workshop)[ws_count - 1]
                j_link = request.form.get('session-link')
                if current_workshop.joining_link2 is None or current_workshop.joining_link2 == '':
                    current_workshop.joining_link2 = j_link
                    flash('Successfully added chief!', 'success')
                elif current_workshop.joining_link3 is None or current_workshop.joining_link3 == '':
                    current_workshop.joining_link3 = j_link
                    flash('Successfully added chief!', 'success')
                elif current_workshop.joining_link4 is None or current_workshop.joining_link4 == '':
                    current_workshop.joining_link4 = j_link
                    flash('Successfully added chief!', 'success')
                else:
                    flash("Sorry! Couldn't add Chief!", 'error')
                db.session.commit()

            if request.form.get('yt'):
                recording_link = request.form.get('yt')
                if current_workshop.yt_p1_id is None or current_workshop.yt_p1_id == '':
                    current_workshop.yt_p1_id = recording_link
                    flash('Successfully added Chief!', 'success')
                elif current_workshop.yt_p2_id is None or current_workshop.yt_p2_id == '':
                    current_workshop.yt_p2_id = recording_link
                    flash('Successfully added Chief!', 'success')
                elif current_workshop.yt_p3_id is None or current_workshop.yt_p3_id == '':
                    current_workshop.yt_p3_id = recording_link
                    flash('Successfully added Chief!', 'success')
                elif current_workshop.yt_p4_id is None or current_workshop.yt_p4_id == '':
                    current_workshop.yt_p4_id = recording_link
                    flash('Successfully added Chief!', 'success')
                else:
                    flash("Sorry! Couldn't Add Chief!", 'error')
                db.session.commit()

            if request.form.get('close') and request.form.get('close') == 'shut-reg-door':
                result = db.session.query(Payment).filter_by(ws_name=current_ws_name).all()
                collection = 0
                for fee in result:
                    collection += int(fee.amount)
                current_workshop.gross_revenue = collection
                current_workshop.reg_close = today_date
                current_workshop.strength = len(current_workshop.participants)
                db.session.commit()
            if request.form.get('submit') and request.form.get('submit') == 'mail-promo':
                recipients = []
                current_workshop = db.session.query(Workshop)[db.session.query(Workshop).count() - 1]
                result = db.session.query(User)
                for user in result:
                    recipients.append(user.email)
                result2 = db.session.query(Query)
                if result2.count() > 0:
                    for user in result2:
                        if user.email not in recipients:
                            recipients.append(user.email)
                if current_workshop.details:
                    d = current_workshop.details
                    html = render_template('mails/ws_promotion.html',
                                           cat=d.category,
                                           topic=current_ws_topic,
                                           brief=d.brief,
                                           sessions=d.sessions,
                                           st1=d.subtopic1,
                                           st2=d.subtopic2,
                                           st3=d.subtopic3,
                                           st4=d.subtopic4,
                                           st5=d.subtopic5,
                                           st6=d.subtopic6,
                                           st7=d.subtopic7,
                                           st8=d.subtopic8,
                                           st9=d.subtopic9,
                                           des=d.description
                                           )
                    image_dict = {
                        'file': ['fb.png', 'insta.png', 'twitter.png'],
                        'path': ['social-icons', 'social-icons', 'social-icons'],
                    }
                    send_email_school('NEW WORKSHOP ENROLLMENT OPEN', recipients, '', html, image_dict)
                    flash('Mailed successfully, Chief!', 'success')
                else:
                    flash('No workshop-details found, Chief!', 'error')

            if request.form.get('submit') and request.form.get('submit') == 'wa-promo':
                message = f"Dear [name],\nEnrollment/Registration to the new workshop: {current_ws_topic} is open.\n" \
                          f"Know more and get enrolled/registered at {url_for('workshops')}\n"
                number_list = []
                name_list = []

                users = db.session.query(User)
                query = db.session.query(Query)

                for user in users:
                    if user.whatsapp:
                        number_list.append(user.whatsapp)
                    else:
                        number_list.append(user.phone)
                    name_list.append(user.name.split()[0])
                for q in query:
                    if q.whatsapp:
                        number_list.append(q.whatsapp)
                    else:
                        number_list.append(q.phone)
                    name_list.append(q.name.split()[0])
                send_wa_msg_by_list(message, number_list, name_list)

            if request.form.get('submit') and request.form.get('submit') == 'wa-mail-promo':
                message = f"Dear [name],\nEnrollment/Registration to the new workshop: {current_ws_topic} is open.\n" \
                          f"Know more and get enrolled/registered at {url_for('workshops')}\n"
                number_list = []
                name_list = []

                users = db.session.query(User)
                query = db.session.query(Query)

                for user in users:
                    if user.whatsapp:
                        number_list.append(user.whatsapp)
                    else:
                        number_list.append(user.phone)
                    name_list.append(user.name.split()[0])
                if query.count() > 0:
                    for q in query:
                        if q.whatsapp:
                            number_list.append(q.whatsapp)
                        else:
                            number_list.append(q.phone)
                        name_list.append(q.name.split()[0])

                recipients = []
                current_workshop = db.session.query(Workshop)[db.session.query(Workshop).count() - 1]
                subject = 'NEW WORKSHOP ENROLLMENT OPEN'
                result = db.session.query(User)
                for user in result:
                    recipients.append(user.email)
                result2 = db.session.query(Query)
                for user in result2:
                    if user.email not in recipients:
                        recipients.append(user.email)
                if current_workshop.details:
                    d = current_workshop.details
                    html = render_template('mails/ws_promotion.html',
                                           cat=d.category,
                                           topic=current_ws_topic,
                                           brief=d.brief,
                                           sessions=d.sessions,
                                           st1=d.subtopic1,
                                           st2=d.subtopic2,
                                           st3=d.subtopic3,
                                           st4=d.subtopic4,
                                           st5=d.subtopic5,
                                           st6=d.subtopic6,
                                           st7=d.subtopic7,
                                           st8=d.subtopic8,
                                           st9=d.subtopic9,
                                           des=d.description
                                           )
                    image_dict = {
                        'file': ['fb.png', 'insta.png', 'twitter.png'],
                        'path': ['social-icons', 'social-icons', 'social-icons'],
                    }
                    send_email_school_and_wa_msg_by_list(subject, recipients, '', html, image_dict, message,
                                                         number_list, name_list)
                    flash('Mailed and messaged successfully, Chief!', 'success')

            if request.form.get('submit') and request.form.get('submit') == 'mail-last-rem':
                current_workshop = db.session.query(Workshop)[db.session.query(Workshop).count() - 1]
                if current_workshop.details:
                    d = current_workshop.details
                    html = render_template('mails/enrollment_reminder.html',
                                           cat=d.category,
                                           topic=current_ws_topic,
                                           brief=d.brief,
                                           sessions=d.sessions,
                                           st1=d.subtopic1,
                                           st2=d.subtopic2,
                                           st3=d.subtopic3,
                                           st4=d.subtopic4,
                                           st5=d.subtopic5,
                                           st6=d.subtopic6,
                                           st7=d.subtopic7,
                                           st8=d.subtopic8,
                                           st9=d.subtopic9,
                                           des=d.description
                                           )
                    image_dict = {
                        'file': ['fb.png', 'insta.png', 'twitter.png'],
                        'path': ['social-icons', 'social-icons', 'social-icons'],
                    }
                    subject = 'LAST DAY'
                    enrolled_user_list = []
                    recipients = []
                    enrolled_users = current_workshop.participants
                    for user in enrolled_users:
                        enrolled_user_list.append(user.email)
                    result = db.session.query(User)
                    result2 = db.session.query(Query)
                    for user in result:
                        if user.email not in enrolled_user_list and user.email not in recipients:
                            recipients.append(user.email)
                    if result2.count() > 0:
                        for user in result2:
                            if user.email not in enrolled_user_list and user.email not in recipients:
                                recipients.append(user.email)
                    send_email_school(subject, recipients, '', html, image_dict)

            if request.form.get('submit') and request.form.get('submit') == 'wa-last-rem':
                message = f"Dear [name],\n Today is the last day for enrollment/registration to the workshop: {current_ws_topic}.\n" \
                          f"Know more and get enrolled/registered now at {url_for('workshops')}\n"
                number_list = []
                name_list = []
                enrolled_numbers = []

                result = current_workshop.participants
                for user in result:
                    if user.whatsapp:
                        enrolled_numbers.append(user.whatsapp)
                    else:
                        enrolled_numbers.append(user.phone)
                users = db.session.query(User)
                query = db.session.query(Query)

                for user in users:
                    if user.whatsapp and user.whatsapp not in number_list and user.whatsapp not in enrolled_numbers:
                        number_list.append(user.whatsapp)
                    elif user.phone not in number_list and user.phone not in enrolled_numbers:
                        number_list.append(user.phone)
                        name_list.append()
                    name_list.append(user.name.split()[0])
                if query.count() > 0:
                    for user in query:
                        if user.whatsapp and user.whatsapp not in number_list and user.whatsapp not in enrolled_numbers:
                            number_list.append(user.whatsapp)
                        elif user.phone not in number_list and user.phone not in enrolled_numbers:
                            number_list.append(user.phone)
                        name_list.append(user.name.split()[0])

                send_wa_msg_by_list(message, number_list, name_list)

            if request.form.get('submit') and request.form.get('submit') == 'wa-mail-last-rem':
                current_workshop = db.session.query(Workshop)[db.session.query(Workshop).count() - 1]
                if current_workshop.details:
                    d = current_workshop.details
                    html = render_template('mails/enrollment_reminder.html',
                                           cat=d.category,
                                           topic=current_ws_topic,
                                           brief=d.brief,
                                           sessions=d.sessions,
                                           st1=d.subtopic1,
                                           st2=d.subtopic2,
                                           st3=d.subtopic3,
                                           st4=d.subtopic4,
                                           st5=d.subtopic5,
                                           st6=d.subtopic6,
                                           st7=d.subtopic7,
                                           st8=d.subtopic8,
                                           st9=d.subtopic9,
                                           des=d.description
                                           )
                    image_dict = {
                        'file': ['fb.png', 'insta.png', 'twitter.png'],
                        'path': ['social-icons', 'social-icons', 'social-icons'],
                    }
                    subject = 'LAST DAY'
                    enrolled_user_list = []
                    recipients = []
                    enrolled_users = current_workshop.participants
                    for user in enrolled_users:
                        enrolled_user_list.append(user.email)
                    result = db.session.query(User)
                    result2 = db.session.query(Query)
                    for user in result:
                        if user.email not in enrolled_user_list and user.email not in recipients:
                            recipients.append(user.email)
                    if result2.count() > 0:
                        for user in result2:
                            if user.email not in enrolled_user_list and user.email not in recipients:
                                recipients.append(user.email)

                    message = f"Dear [name],\n Today is the last day for enrollment/registration to the workshop: {current_ws_topic}.\n" \
                              f"Know more and get enrolled/registered now at {url_for('workshops')}\n"
                    number_list = []
                    name_list = []
                    enrolled_numbers = []

                    result = current_workshop.participants
                    for user in result:
                        if user.whatsapp:
                            enrolled_numbers.append(user.whatsapp)
                        else:
                            enrolled_numbers.append(user.phone)
                    users = db.session.query(User)
                    query = db.session.query(Query)

                    for user in users:
                        if user.whatsapp and user.whatsapp not in number_list and user.whatsapp not in enrolled_numbers:
                            number_list.append(user.whatsapp)
                        elif user.phone not in number_list and user.phone not in enrolled_numbers:
                            number_list.append(user.phone)
                            name_list.append(user.name.split()[0])
                        name_list.append(user.name.split()[0])
                    if query.count() > 0:
                        for user in query:
                            if user.whatsapp and user.whatsapp not in number_list and user.whatsapp not in enrolled_numbers:
                                number_list.append(user.whatsapp)
                            elif user.phone not in number_list and user.phone not in enrolled_numbers:
                                number_list.append(user.phone)
                            name_list.append(user.name.split()[0])

                send_email_school_and_wa_msg_by_list(subject, recipients, '', html, image_dict, message, number_list,
                                                     name_list)

            if request.form.get('submit') and request.form.get('submit') == 'mail-link':
                current_workshop = db.session.query(Workshop)[db.session.query(Workshop).count()-1]

                if not current_workshop.joining_link2 or current_workshop.joining_link2 == '':
                    joining_link = current_workshop.joining_link
                elif not current_workshop.joining_link3 or current_workshop.joining_link3 == '':
                    joining_link = current_workshop.joining_link2
                elif not current_workshop.joining_link4 or current_workshop.joining_link4 == '':
                    joining_link = current_workshop.joining_link3
                else:
                    joining_link = current_workshop.joining_link4
                subject = 'JOINING LINK'
                recipients = []
                result = current_workshop.participants
                for user in result:
                    recipients.append(user.email)
                recipients = list(set(recipients))
                body = f"The Workshop session joining link is below:\n{joining_link}"
                send_email_school(subject, recipients, body, '', '')

            if request.form.get('submit') and request.form.get('submit') == 'wa-link':
                current_workshop = db.session.query(Workshop)[db.session.query(Workshop).count() - 1]
                if not current_workshop.joining_link2 or current_workshop.joining_link2 == '':
                    joining_link = current_workshop.joining_link
                elif not current_workshop.joining_link3 or current_workshop.joining_link3 == '':
                    joining_link = current_workshop.joining_link2
                elif not current_workshop.joining_link4 or current_workshop.joining_link4 == '':
                    joining_link = current_workshop.joining_link3
                else:
                    joining_link = current_workshop.joining_link4
                wa_msg = f"The workshop session joining link is below:\n{joining_link}\n"
                num_list = []
                names_list = []
                result = current_workshop.participants
                result = list(set(result))
                for user in result:
                    if user.whatsapp:
                        num_list.append(user.whatsapp)
                    else:
                        num_list.append(user.phone)
                    names_list.append(user.name.split()[0])

                send_wa_msg_by_list(wa_msg, num_list, names_list)

            if request.form.get('submit') and request.form.get('submit') == 'wa-mail-link':
                current_workshop = db.session.query(Workshop)[db.session.query(Workshop).count() - 1]

                if not current_workshop.joining_link2 or current_workshop.joining_link2 == '':
                    joining_link = current_workshop.joining_link
                elif not current_workshop.joining_link3 or current_workshop.joining_link3 == '':
                    joining_link = current_workshop.joining_link2
                elif not current_workshop.joining_link4 or current_workshop.joining_link4 == '':
                    joining_link = current_workshop.joining_link3
                else:
                    joining_link = current_workshop.joining_link4
                subject = 'JOINING LINK'
                recipients = []
                result = current_workshop.participants
                for user in result:
                    recipients.append(user.email)
                recipients = list(set(recipients))
                body = f"The Workshop session joining link is below:\n{joining_link}"

                wa_msg = f"The workshop session joining link is below:\n{joining_link}\n"
                num_list = []
                names_list = []
                result = current_workshop.participants
                result = list(set(result))
                for user in result:
                    if user.whatsapp:
                        num_list.append(user.whatsapp)
                    else:
                        num_list.append(user.phone)
                    names_list.append(user.name.split()[0])

                send_email_school_and_wa_msg_by_list(subject, recipients, body, '', '', wa_msg, num_list, names_list)

            if request.form.get('submit') and request.form.get('submit') == 'mail-s-rem':
                current_workshop = db.session.query(Workshop)[db.session.query(Workshop).count()-1]
                students = current_workshop.participants
                subject = 'WORKSHOP SESSION STARTED'
                image_dict = {
                    'file': ['fb.png', 'insta.png', 'twitter.png'],
                    'path': ['social-icons', 'social-icons', 'social-icons'],
                }
                if not current_workshop.joining_link2 or current_workshop.joining_link2 == '':
                    joining_link = current_workshop.joining_link
                elif not current_workshop.joining_link3 or current_workshop.joining_link3 == '':
                    joining_link = current_workshop.joining_link2
                elif not current_workshop.joining_link4 or current_workshop.joining_link4 == '':
                    joining_link = current_workshop.joining_link3
                else:
                    joining_link = current_workshop.joining_link4
                for user in students:
                    name = user.name.split()[0]
                    recipients = [user.email]
                    html = render_template('mails/session_joining_reminder.html', name=name, joining_link=joining_link)
                    send_email_school(subject, recipients, '', html, image_dict)

            if request.form.get('submit') and request.form.get('submit') == 'wa-s-rem':
                current_workshop = db.session.query(Workshop)[db.session.query(Workshop).count() - 1]
                students = current_workshop.participants
                if not current_workshop.joining_link2 or current_workshop.joining_link2 == '':
                    joining_link = current_workshop.joining_link
                elif not current_workshop.joining_link3 or current_workshop.joining_link3 == '':
                    joining_link = current_workshop.joining_link2
                elif not current_workshop.joining_link4 or current_workshop.joining_link4 == '':
                    joining_link = current_workshop.joining_link3
                else:
                    joining_link = current_workshop.joining_link4
                for user in students:
                    name_list = [user.name.split()[0]]
                    wa_msg = f"Dear{user.name.split()[0]},\nThe workshop session has started. If you've not joined " \
                             f"yet please join it by clicking below.\n{joining_link}\n"
                    if user.whatsapp:
                        num_list = [user.whatsapp]
                    else:
                        num_list = [user.phone]
                    send_wa_msg_by_list(wa_msg, num_list, name_list)

            if request.form.get('submit') and request.form.get('submit') == 'wa-mail-s-rem':
                current_workshop = db.session.query(Workshop)[db.session.query(Workshop).count() - 1]
                students = current_workshop.participants
                if not current_workshop.joining_link2 or current_workshop.joining_link2 == '':
                    joining_link = current_workshop.joining_link
                elif not current_workshop.joining_link3 or current_workshop.joining_link3 == '':
                    joining_link = current_workshop.joining_link2
                elif not current_workshop.joining_link4 or current_workshop.joining_link4 == '':
                    joining_link = current_workshop.joining_link3
                else:
                    joining_link = current_workshop.joining_link4
                subject = 'WORKSHOP SESSION STARTED'
                image_dict = {
                    'file': ['fb.png', 'insta.png', 'twitter.png'],
                    'path': ['social-icons', 'social-icons', 'social-icons'],
                }

                for user in students:
                    name = user.name.split()[0]
                    name_list = [name]
                    if user.whatsapp:
                        num_list = [user.whatsapp]
                    else:
                        num_list = [user.phone]
                    recipients = [user.email]
                    wa_msg = f"Dear{user.name.split()[0]},\nThe workshop session has started. If you've not joined " \
                             f"yet please join it by clicking below.\n{joining_link}\n"
                    html = render_template('mails/session_joining_reminder.html', name=name, joining_link=joining_link)
                    send_email_school_and_wa_msg_by_list(subject, recipients, '', html, image_dict, wa_msg, num_list, name_list)

            if request.form.get('submit') and request.form.get('submit') == 'certificate-dist':
                current_workshop = db.session.query(Workshop)[db.session.query(Workshop).count()-1]
                participants = current_workshop.participants
                cat = current_workshop.details.category
                subject = 'CERTIFICATE DOWNLOAD'
                image_dict = {
                    'file': ['fb.png', 'insta.png', 'twitter.png'],
                    'path': ['social-icons', 'social-icons', 'social-icons'],
                }
                for participant in participants:
                    html = render_template('mails/certificate_download.html', name=participant.name.split()[0], download_link='https://writart.com', category=cat)
                    recipients = [participant.email]
                    send_email_school(subject, recipients, '', html, image_dict)

            if request.form.get('submit') and request.form.get('submit') == 'csv-exp-cert':
                name_dict = {
                    'Name': []
                }
                current_workshop = db.session.query(Workshop)[db.session.query(Workshop).count()-1]
                participants = current_workshop.participants
                for participant in participants:
                    if participant.sex == 'male':
                        name_dict['Name'].append(f"Mr. {participant.name}")
                    elif participant.sex == 'female':
                        name_dict['Name'].append(f"Ms. {participant.name}")
                    else:
                        name_dict['Name'].append(participant.name)
                df = pd.DataFrame.from_dict(name_dict)
                file = 'static/files/internal_operations/certificate_name_list.csv'
                if os.path.exists(file):
                    os.remove(file)
                df.to_csv(file, index=False)

            if request.form.get('submit') and request.form.get('submit') == 'download-cert-name-csv':
                file = 'static/files/internal_operations/certificate_name_list.csv'
                if os.path.exists(file) and os.path.isfile(file):
                    current_workshop_name = db.session.query(Workshop)[db.session.query(Workshop).count()-1].name
                    file_name = 'certificate_name_list_' + current_workshop_name
                    return send_file(path_or_file=file, as_attachment=True, download_name=file_name)
                else:
                    flash("Oops Chief! The file doesn't exist!", "error")

            if request.form.get('submit') and request.form.get('submit') == 'upload_files':
                allowed_extensions = {'pdf', 'jpg'}
                current_workshop = db.session.query(Workshop)[db.session.query(Workshop).count()-1]
                participants = current_workshop.participants

                if 'file' not in request.files:
                    flash('No file part', 'error')
                    return redirect(request.url)
                files = request.files.getlist('file')

                db.session.query(Tools).filter_by(keyword='certificate').one().data = db.session.query(Workshop)[db.session.query(Workshop).count()-1].topic

                name_list = []
                folder_name_list = []
                for participant in participants:
                    folder_name = participant.name.split()[0] + str(participant.id)
                    folder_name_list.append(folder_name)
                    name_list.append(participant.name.split()[0])

                    folder = f'static/files/users/{folder_name}/certificates'
                    if not os.path.exists(folder):
                        os.makedirs(folder)
                cnt = 0
                for file in files:
                    if file.filename == '':
                        flash('No selected file', 'error')
                        return redirect(request.url)
                    if file and allowed_file(file.filename, allowed_extensions):
                        # filename = secure_filename(file.filename)
                        file_name = f"{current_workshop.name}-{name_list[cnt]}.pdf"
                        path = f'static/files/users/{folder_name_list[cnt]}/certificates'

                        file.save(os.path.join(path, file_name))
                        cnt += 1
                return redirect(url_for('manager.home'))

        return render_template('manager.html', logged_in=current_user.is_authenticated)
    else:
        return render_template('admin_area.html', logged_in=current_user.is_authenticated)