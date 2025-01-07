import os
import pandas as pd
from flask import Blueprint, render_template, request, flash, redirect, url_for, send_file
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from extensions import db, admin_only
from models.videos import Demo
from operations.messenger import send_email_school, send_wa_msg_by_list, send_email_school_and_wa_msg_by_list
from models.payment import Payment
from models.query import Query
from models.tool import Tools
from models.member import Member, Workshop, Role
from models.workshop_details import WorkshopDetails
from operations.miscellaneous import allowed_file
from routes.account import today_date

manager = Blueprint('manager', __name__, static_folder='static', template_folder='templates/manager')


@manager.route('/', methods=['GET', 'POST'])
@login_required
def home():
    global current_ws_name, current_ws, current_workshop, current_ws_topic
    current_ws_name = db.session.query(Tools).filter_by(keyword='current_workshop').one_or_none().data
    current_ws = current_workshop = db.session.query(Workshop).filter_by(name=current_ws_name).one_or_none()
    current_ws_topic = current_ws.topic

    if db.session.query(Role).filter(Role.name == 'admin').scalar() in current_user.role:
        if request.method == 'POST':
            if request.form.get('current_ws'):
                db.session.query(Tools).filter_by(keyword='current_workshop').first().data = request.form.get('current_ws')
                db.session.commit()
            if request.form.get('open-reg'):
                db.session.query(Tools).filter_by(keyword='open_reg').one().data = 'Done'
                db.session.query(Tools).filter_by(keyword='promotion').one().data = 'Pending'
                db.session.query(Tools).filter_by(keyword='reminder').one().data = 'Pending'
                db.session.query(Tools).filter_by(keyword='close_reg').one().data = 'Pending'
                db.session.query(Tools).filter_by(keyword='certificate_distribution').one().data = 'Pending'
                db.session.query(Workshop).filter_by(name=current_ws_name).one().reg_start = today_date
                db.session.query(Tools).filter_by(keyword='reg_status').one().data = 'open'
                db.session.commit()
                flash('Registration opened boss!', 'success')
            if request.form.get('name'):
                result = db.session.query(Workshop).filter_by(name=request.form.get('name')).first()
                if result:
                    flash("Chief! The workshop already exist!", "error")
                    return redirect(request.url)
                else:
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
                    time = request.form.get('time')
                    instructor_ = request.form.get('instructor')
                    session_link = request.form.get('link')
                    entry = Workshop(
                        name=name,
                        topic=topic,
                        date=date_,
                        time=time,
                        instructor=instructor_,
                        joining_link=session_link,
                    )
                    db.session.add(entry)
                    db.session.query(Tools).filter_by(keyword='reg_status').one().data = 'pending'
                    db.session.query(Tools).filter_by(keyword='open_reg').first().data = 'Pending'
                    db.session.commit()
                    entry2 = WorkshopDetails(
                        workshop=db.session.query(Workshop).filter_by(name=name).one()
                    )
                    db.session.add(entry2)
                    db.session.commit()
                    flash('New Workshop Added', 'success')
                    return redirect(url_for('manager.home'))

            if request.form.get('category'):
                ws_name = request.form.get('ws_name')
                workshop = db.session.query(Workshop).filter_by(name=ws_name).first()
                details = workshop.details
                details.category = request.form.get('category'),
                details.brief = request.form.get('brief'),
                details.sessions = request.form.get('sessions'),
                details.subtopic1 = request.form.get('st1'),
                details.subtopic2 = request.form.get('st2'),
                details.subtopic3 = request.form.get('st3'),
                details.subtopic4 = request.form.get('st4'),
                details.subtopic5 = request.form.get('st5'),
                details.subtopic6 = request.form.get('st6'),
                details.subtopic7 = request.form.get('st7'),
                details.subtopic8 = request.form.get('st8'),
                details.subtopic9 = request.form.get('st9'),
                details.description = request.form.get('description'),
                details.req1 = request.form.get('req1'),
                details.req2 = request.form.get('req2'),
                details.req3 = request.form.get('req3'),
                details.req4 = request.form.get('req4'),
                details.req5 = request.form.get('req5'),
                details.req6 = request.form.get('req6'),
                details.req7 = request.form.get('req7'),
                details.req8 = request.form.get('req8'),
                details.req9 = request.form.get('req9'),
                details.result1 = request.form.get('result1'),
                details.result2 = request.form.get('result2'),
                details.result3 = request.form.get('result3'),
                details.result4 = request.form.get('result4'),
                details.result5 = request.form.get('result5'),
                details.result6 = request.form.get('result6'),
                details.result7 = request.form.get('result7'),
                details.result8 = request.form.get('result8'),
                details.result9 = request.form.get('result9'),
                details.cover = f"{current_ws_name}/cover.jpg",
                details.thumbnail = f"{current_ws_name}/thumbnail.jpg",
                details.photo1 = f'{current_ws_name}/p1',
                details.photo2 = f'{current_ws_name}/p2',
                details.photo3 = f'{current_ws_name}/p3',
                try:
                    db.session.commit()
                    flash('Workshop details added successfully, Chief!', 'success')
                except:
                    flash("Sorry, Couldn't add, Chief!", "error")

            if request.form.get('submit') and request.form.get('submit') == 'upload_photos':
                allowed_extensions = {'png', 'jpg'}

                if 'file' not in request.files:
                    flash('No file part', 'error')
                    return redirect(request.url)
                files = request.files.getlist('file')

                folder_name = request.form.get('workshop_name')
                folder = f"./static/images/workshops/{folder_name}"
                if not os.path.exists(folder):
                    os.makedirs(folder)
                for file in files:
                    if file.filename == '':
                        flash('No selected file', 'error')
                        return redirect(request.url)
                    if file and allowed_file(file.filename, allowed_extensions):
                        filename = secure_filename(file.filename)
                        file.save(f"{folder}/{filename}")
                        flash('Chief! Images uploaded successfully!', 'success')

            if request.form.get('session-link'):
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
                db.session.query(Tools).filter_by(keyword='reg_status').one().data = 'close'
                db.session.query(Tools).filter_by(keyword='close_reg').one().data = 'Done'
                db.session.commit()

            if request.form.get('add_demo') == 'demo':
                title = request.form.get('title')
                level = request.form.get('level')
                caption = request.form.get('caption')
                video_id1 = request.form.get('vid_id1')
                video_id2 = request.form.get('vid_id2')
                video_id3 = request.form.get('vid_id3')
                tags = request.form.get('tags')

                demo_url_list = []
                result = db.session.query(Demo)
                for r in result:
                    demo_url_list.append(r.vid_id1)

                if video_id1 not in demo_url_list:
                    try:
                        entry = Demo(
                            title=title,
                            caption=caption,
                            vid_id1=video_id1,
                            vid_id2=video_id2,
                            vid_id3=video_id3,
                            tags=tags,
                            date=today_date,
                            level=level,
                            creator_id=current_user.id
                        )
                        db.session.add(entry)
                        db.session.commit()
                        flash("Chief! Demo successfully added!", "success")
                    except Exception as e:
                        print(e)
                        flash("I'm sorry Chief! Some error occurred!", "error")

            if request.form.get('submit') and request.form.get('submit') == 'mail-promo':
                recipients = []
                current_workshop = db.session.query(Workshop)[db.session.query(Workshop).count() - 1]
                result = db.session.query(Member)
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
                    send_email_school('NEW WORKSHOP ENROLLMENT OPEN', recipients, '', html, '')
                    db.session.query(Tools).filter_by(keyword='promotion').one().data = 'Done'
                    flash('Mailed successfully, Chief!', 'success')
                else:
                    flash('No workshop-details found, Chief!', 'error')

            if request.form.get('submit') and request.form.get('submit') == 'wa-promo':
                message = f"Dear [name],\nEnrollment/Registration to the new workshop: {current_ws_topic} is open.\n" \
                          f"Know more and get enrolled/registered at {url_for('workshops')}\n"
                number_list = []
                name_list = []

                users = db.session.query(Member)
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
                db.session.query(Tools).filter_by(keyword='promotion').one().data = 'Done'

            if request.form.get('submit') and request.form.get('submit') == 'wa-mail-promo':
                message = f"Dear [name],\nEnrollment/Registration to the new workshop: {current_ws_topic} is open.\n" \
                          f"Know more and get enrolled/registered at {url_for('workshops')}\n"
                number_list = []
                name_list = []

                users = db.session.query(Member)
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
                subject = 'NEW WORKSHOP ENROLLMENT OPEN'
                result = db.session.query(Member)
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
                    send_email_school_and_wa_msg_by_list(subject, recipients, '', html, '', message,
                                                         number_list, name_list)
                    db.session.query(Tools).filter_by(keyword='promotion').one().data = 'Done'
                    flash('Mailed and messaged successfully, Chief!', 'success')

            if request.form.get('submit') and request.form.get('submit') == 'mail-last-rem':
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
                    result = db.session.query(Member)
                    result2 = db.session.query(Query)
                    for user in result:
                        if user.email not in enrolled_user_list and user.email not in recipients:
                            recipients.append(user.email)
                    if result2.count() > 0:
                        for user in result2:
                            if user.email not in enrolled_user_list and user.email not in recipients:
                                recipients.append(user.email)
                    send_email_school(subject, recipients, '', html, '')
                    db.session.query(Tools).filter_by(keyword='reminder').one().data = 'Done'

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
                users = db.session.query(Member)
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
                db.session.query(Tools).filter_by(keyword='reminder').one().data = 'Done'

            if request.form.get('submit') and request.form.get('submit') == 'wa-mail-last-rem':
                # current_workshop = db.session.query(Workshop)[db.session.query(Workshop).count() - 1]
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
                    result = db.session.query(Member)
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
                    users = db.session.query(Member)
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

                send_email_school_and_wa_msg_by_list(subject, recipients, '', html, '', message, number_list,
                                                     name_list)
                db.session.query(Tools).filter_by(keyword='reminder').one().data = 'Done'

            if request.form.get('submit') and request.form.get('submit') == 'mail-link':

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
                    send_email_school(subject, recipients, '', html, '')

            if request.form.get('submit') and request.form.get('submit') == 'wa-s-rem':
                # current_workshop = db.session.query(Workshop)[db.session.query(Workshop).count() - 1]
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
                    send_email_school_and_wa_msg_by_list(subject, recipients, '', html, '', wa_msg, num_list,
                                                         name_list)

            if request.form.get('submit') and request.form.get('submit') == 'certificate-dist':
                participants = current_workshop.participants
                cat = current_workshop.details.category
                subject = 'CERTIFICATE DOWNLOAD'
                image_dict = {
                    'file': ['fb.png', 'insta.png', 'twitter.png'],
                    'path': ['social-icons', 'social-icons', 'social-icons'],
                }
                for participant in participants:
                    html = render_template('mails/certificate_download.html', name=participant.name.split()[0],
                                           download_link='https://writart.com/school/certificate_download', category=cat)
                    recipients = [participant.email]
                    send_email_school(subject, recipients, '', html, '')
                    db.session.query(Tools).filter_by(keyword='certificate_distribution').one().data = 'Done'

            if request.form.get('submit') and request.form.get('submit') == 'csv-exp-cert':
                name_dict = {
                    'Name': []
                }
                participants = current_workshop.participants
                for participant in participants:
                    if participant.sex == 'male':
                        name_dict['Name'].append(f"Mr. {participant.name}")
                    elif participant.sex == 'female':
                        name_dict['Name'].append(f"Ms. {participant.name}")
                    else:
                        name_dict['Name'].append(participant.name)
                df = pd.DataFrame.from_dict(name_dict)
                file = './static/files/internal_operations/certificate_name_list.csv'
                df.to_csv(file, index=False)

            if request.form.get('submit') and request.form.get('submit') == 'download-cert-name-csv':
                file = './static/files/internal_operations/certificate_name_list.csv'
                if os.path.exists(file) and os.path.isfile(file):
                    file_name = 'certificate_name_list_' + current_ws_name + '.csv'
                    return send_file(path_or_file=file, as_attachment=True, download_name=file_name)
                else:
                    flash("Oops Chief! The file doesn't exist!", "error")

            if request.form.get('submit') and request.form.get('submit') == 'upload_files':
                allowed_extensions = {'pdf', 'jpg'}
                participants = current_workshop.participants

                if 'file' not in request.files:
                    flash('No file part', 'error')
                    return redirect(request.url)
                files = request.files.getlist('file')
                db.session.query(Tools).filter_by(keyword='certificate').one().data = current_ws_topic

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
                        path = f'../static/files/users/{folder_name_list[cnt]}/certificates'

                        file.save(os.path.join(path, file_name))
                        cnt += 1
                return redirect(url_for('manager.home'))
            if request.form.get('submit') and request.form.get('submit') == 'upload_artworks':
                allowed_extensions = {'jpg'}

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
                        path = 'static/files/users/Shwetabh1/artworks'
                        if not os.path.exists(path):
                            os.makedirs(path)
                        file.save(os.path.join(path, filename))
                return redirect(url_for('manager.home'))

        open_reg = db.session.query(Tools).filter_by(keyword='open_reg').one().data
        promotion = db.session.query(Tools).filter_by(keyword='promotion').one().data
        reminder = db.session.query(Tools).filter_by(keyword='reminder').one().data
        close_reg = db.session.query(Tools).filter_by(keyword='close_reg').one().data
        certificate_distribution = db.session.query(Tools).filter_by(keyword='certificate_distribution').one().data
        workshops = db.session.query(Workshop)
        upcoming_ws_dict = {
            'ws': [],
            'details': []
        }
        for workshop in workshops:
            if not workshop.reg_start or workshop.reg_start == '':
                workshop_dict = {
                    'name': workshop.name,
                    'topic': workshop.topic,
                    'instructor': workshop.instructor
                }
                upcoming_ws_dict['ws'].append(workshop_dict)
                if not workshop.details.brief:
                    details_dict = {
                        'status': 'Empty',
                        'category': '',
                        'brief': '',
                        'sessions': '',
                        'subtopic1': '',
                        'subtopic2': '',
                        'subtopic3': '',
                        'subtopic4': '',
                        'subtopic5': '',
                        'subtopic6': '',
                        'subtopic7': '',
                        'subtopic8': '',
                        'subtopic9': '',
                        'description': '',
                        'req1': '',
                        'req2': '',
                        'req3': '',
                        'req4': '',
                        'req5': '',
                        'req6': '',
                        'req7': '',
                        'req8': '',
                        'req9': '',
                        'r1': '',
                        'r2': '',
                        'r3': '',
                        'r4': '',
                        'r5': '',
                        'r6': '',
                        'r7': '',
                        'r8': '',
                        'r9': '',
                    }
                    upcoming_ws_dict['details'].append(details_dict)
                else:
                    details_dict = {
                        'status': 'Exists',
                        'category': workshop.details.category,
                        'brief': workshop.details.brief,
                        'sessions': workshop.details.sessions,
                        'subtopic1': workshop.details.subtopic1,
                        'subtopic2': workshop.details.subtopic2,
                        'subtopic3': workshop.details.subtopic3,
                        'subtopic4': workshop.details.subtopic4,
                        'subtopic5': workshop.details.subtopic5,
                        'subtopic6': workshop.details.subtopic6,
                        'subtopic7': workshop.details.subtopic7,
                        'subtopic8': workshop.details.subtopic8,
                        'subtopic9': workshop.details.subtopic9,
                        'description': workshop.details.description,
                        'req1': workshop.details.req1,
                        'req2': workshop.details.req2,
                        'req3': workshop.details.req3,
                        'req4': workshop.details.req4,
                        'req5': workshop.details.req5,
                        'req6': workshop.details.req6,
                        'req7': workshop.details.req7,
                        'req8': workshop.details.req8,
                        'req9': workshop.details.req9,
                        'r1': workshop.details.result1,
                        'r2': workshop.details.result2,
                        'r3': workshop.details.result3,
                        'r4': workshop.details.result4,
                        'r5': workshop.details.result5,
                        'r6': workshop.details.result6,
                        'r7': workshop.details.result7,
                        'r8': workshop.details.result8,
                        'r9': workshop.details.result9,
                    }
                    upcoming_ws_dict['details'].append(details_dict)

        count = len(upcoming_ws_dict['ws'])
        count_list = []
        for i in range(count):
            count_list.append(i)

        return render_template('manager.html', logged_in=current_user.is_authenticated,
                               current_ws_name=current_ws_name, open_reg=open_reg, promotion=promotion,
                               reminder=reminder, close_reg=close_reg,
                               certificate_distribution=certificate_distribution, upcoming_ws_dict=upcoming_ws_dict,
                               count=count, count_list=count_list)
    else:
        return render_template('admin_area.html', logged_in=current_user.is_authenticated)


@login_required
@admin_only
@manager.route('/adv_operations')
def adv_operations():
    admin = db.session.query(Role).filter_by(name='admin').one_or_none()
    return render_template('advanced_operations.html', logged_in=current_user.is_authenticated, admin=admin)


@login_required
@admin_only
@manager.route('/visualization')
def visualization():
    admin = db.session.query(Role).filter_by(name='admin').one_or_none()
    return render_template('visualization.html', logged_in=current_user.is_authenticated, admin=admin)


@login_required
@admin_only
@manager.route('/role_management', methods=['GET', 'POST'])
def role_management():
    student = db.session.query(Role).filter_by(name='student').one_or_none()
    admin = db.session.query(Role).filter_by(name='admin').one_or_none()
    animation_admin = db.session.query(Role).filter_by(name='animation_admin').one_or_none()
    editor = db.session.query(Role).filter_by(name='editor').one_or_none()
    blogger = db.session.query(Role).filter_by(name='blogger').one_or_none()
    artist = db.session.query(Role).filter_by(name='artist').one_or_none()
    customer = db.session.query(Role).filter_by(name='customer').one_or_none()
    client = db.session.query(Role).filter_by(name='client').one_or_none()
    instructor = db.session.query(Role).filter_by(name='instructor').one_or_none()
    if request.method == 'POST':
        email = request.form.get('email')
        user = db.session.query(Member).filter_by(email=email).one_or_none()
        if request.form.get('role') == 'student' and student not in user.role:
            user.role.append(student)
            flash(f"{email} has been assigned student role", "success")
        elif request.form.get('role') == 'admin' and admin not in user.role:
            user.role.append(admin)
            flash(f"{email} has been assigned admin role", "success")
        elif request.form.get('role') == 'animation_admin' and animation_admin not in user.role:
            user.role.append(animation_admin)
            flash(f"{email} has been assigned animation_admin role", "success")
        elif request.form.get('role') == 'editor' and editor not in user.role:
            user.role.append(editor)
            flash(f"{email} has been assigned editor role", "success")
        elif request.form.get('role') == 'blogger' and blogger not in user.role:
            user.role.append(blogger)
            flash(f"{email} has been assigned blogger role", "success")
        elif request.form.get('role') == 'artist' and artist not in user.role:
            user.role.append(artist)
            flash(f"{email} has been assigned artist role", "success")
        elif request.form.get('role') == 'customer' and customer not in user.role:
            user.role.append(customer)
            flash(f"{email} has been assigned customer role", "success")
        elif request.form.get('role') == 'client' and client not in user.role:
            user.role.append(client)
            flash(f"{email} has been assigned client role", "success")
        elif request.form.get('role') == 'instructor' and instructor not in user.role:
            user.role.append(instructor)
            flash(f"{email} has been assigned instructor role", "success")
        else:
            flash(f"{email} already has this role!!""success")
        db.session.commit()

        if request.form.get('role') == 'student1' and student in user.role:
            user.role.remove(student)
            flash(f"{email} has been removed from student role", "success")
        elif request.form.get('role') == 'admin1' and admin in user.role:
            user.role.remove(admin)
            flash(f"{email} has been removed from admin role", "success")
        elif request.form.get('role') == 'animation_admin1' and animation_admin in user.role:
            user.role.remove(animation_admin)
            flash(f"{email} has been removed from admin role", "success")
        elif request.form.get('role') == 'editor1' and editor in user.role:
            user.role.remove(editor)
            flash(f"{email} has been removed from editor role", "success")
        elif request.form.get('role') == 'blogger1' and blogger in user.role:
            user.role.remove(blogger)
            flash(f"{email} has been removed from blogger role", "success")
        elif request.form.get('role') == 'artist1' and artist in user.role:
            user.role.remove(artist)
            flash(f"{email} has been removed from artist role", "success")
        elif request.form.get('role') == 'customer1' and customer in user.role:
            user.role.remove(customer)
            flash(f"{email} has been removed from customer role", "success")
        elif request.form.get('role') == 'animation_client1' and client in user.role:
            user.role.remove(client)
            flash(f"{email} has been removed from animation_client role", "success")
        elif request.form.get('role') == 'instructor1' and instructor in user.role:
            user.role.remove(instructor)
            flash(f"{email} has been removed from instructor role", "success")
        db.session.commit()
        return redirect(url_for('manager.role_management'))
    admin = db.session.query(Role).filter_by(name='admin').one_or_none()
    return render_template('role_management.html', logged_in=current_user.is_authenticated, admin=admin)


@manager.route('/modifications', methods=['GET', 'POST'])
def modifications():
    global query
    if request.method == 'POST':
        table = request.form.get('table')
        filter_by = request.form.get('filter_by')
        keyword = request.form.get('filter_keyword')
        change_column = enumerate(request.form.get('change_column'))
        data = request.form.get('data')

        if table == 'member':
            query = db.session.query(Member)
        elif table == 'payment':
            query = db.session.query(Payment)
        elif table == 'query':
            query = db.session.query(Query)
        elif table == 'role':
            query = db.session.query(Role)
        elif table == 'tools':
            query = db.session.query(Tools)
        elif table == 'workshop':
            query = db.session.query(Workshop)

        filter_key = f"{filter_by}='{keyword}'"
        row = query.filter_by(filter_key).one()

    admin = db.session.query(Role).filter_by(name='admin').one_or_none()
    return render_template('modifications.html', admin=admin, logged_in=current_user.is_authenticated)


@manager.route('/log')
def log():
    return render_template('log.html')


