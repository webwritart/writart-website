import os
import pprint
import random
from flask import Blueprint, render_template, request, redirect, flash, send_file, session, url_for
from flask_login import current_user
from extensions import db, current_year
from models.query import Query
from models.tool import Tools
from models.member import Workshop, Role, Member
from models.videos import Demo
from models.workshop_details import WorkshopDetails
from operations.messenger import *
import webbrowser
from datetime import datetime

time_now = datetime.now()

school = Blueprint('school', __name__, static_folder='static', template_folder='templates/school')


@school.route('/', methods=['GET', 'POST'])
def home():
    session['url'] = url_for('school.home')
    admin = db.session.query(Role).filter_by(name='admin').first()
    upcoming_workshop_list = []
    all_interested_emails = []

    current_workshop_name = db.session.query(Tools).filter_by(keyword='current_workshop').scalar().data
    current_workshop = db.session.query(Workshop).filter_by(name=current_workshop_name).scalar()
    current_workshop_details = current_workshop.details

    category = current_workshop_details.category
    sessions = current_workshop_details.sessions
    topic = current_workshop.topic
    brief = current_workshop_details.brief
    sub1 = current_workshop_details.subtopic1
    sub2 = current_workshop_details.subtopic2
    sub3 = current_workshop_details.subtopic3
    sub4 = current_workshop_details.subtopic4
    sub5 = current_workshop_details.subtopic5
    sub6 = current_workshop_details.subtopic6
    sub7 = current_workshop_details.subtopic7
    sub8 = current_workshop_details.subtopic8
    sub9 = current_workshop_details.subtopic9
    sub_list = [sub1, sub2, sub3, sub4, sub5, sub6, sub7, sub8, sub9]
    description = current_workshop_details.description
    rq1 = current_workshop_details.req1
    rq2 = current_workshop_details.req2
    rq3 = current_workshop_details.req3
    rq4 = current_workshop_details.req4
    rq5 = current_workshop_details.req5
    rq6 = current_workshop_details.req6
    rq7 = current_workshop_details.req7
    rq8 = current_workshop_details.req8
    rq9 = current_workshop_details.req9
    req_list = [rq1, rq2, rq3, rq4, rq5, rq6, rq7, rq8, rq9]
    r1 = current_workshop_details.result1
    r2 = current_workshop_details.result2
    r3 = current_workshop_details.result3
    r4 = current_workshop_details.result4
    r5 = current_workshop_details.result5
    r6 = current_workshop_details.result6
    r7 = current_workshop_details.result7
    r8 = current_workshop_details.result8
    r9 = current_workshop_details.result9
    result_list = [r1, r2, r3, r4, r5, r6, r7, r8, r9]
    date = current_workshop.date
    time = current_workshop.time
    s2_date = current_workshop.s2_date
    s3_date = current_workshop.s3_date
    s4_date = current_workshop.s4_date
    s2_time = current_workshop.s2_time
    s3_time = current_workshop.s3_time
    s4_time = current_workshop.s4_time
    if request.method == 'POST':
        if request.form.get('interested-form-hidden-workshop'):
            ws_name = request.form.get('interested-form-hidden-workshop')
            try:
                name = current_user.name
                email = current_user.email
                phone = current_user.phone
                whatsapp = current_user.whatsapp
            except Exception as e:
                print(e)
                name = request.form.get('name')
                email = request.form.get('email')
                phone = request.form.get('phone')
                whatsapp = request.form.get('whatsapp')
            message = request.form.get('message')
            all_interested = db.session.query(Query).filter_by(interested_ws=ws_name)

            for i in all_interested:
                all_interested_emails.clear()
                all_interested_emails.append(i.email)

            if email not in all_interested_emails:
                entry = Query(
                    name=name,
                    email=email,
                    phone=phone,
                    whatsapp=whatsapp,
                    interested_ws=ws_name,
                    message=message
                )
                db.session.add(entry)
                db.session.commit()
                flash("Successfully saved details. We'll notify you when time comes!", "success")
            else:
                print('email found!')

        if request.form.get('know-more') == 'know-more':
            ws = request.form.get('submit')
            main_ws_on_page = db.session.query(Workshop).filter_by(name=ws).first()
            workshop = db.session.query(Workshop).filter_by(name=ws).first()
            workshop_details = workshop.details

            category = workshop_details.category
            sessions = workshop_details.sessions
            topic = workshop.topic
            brief = workshop_details.brief
            sub1 = workshop_details.subtopic1
            sub2 = workshop_details.subtopic2
            sub3 = workshop_details.subtopic3
            sub4 = workshop_details.subtopic4
            sub5 = workshop_details.subtopic5
            sub6 = workshop_details.subtopic6
            sub7 = workshop_details.subtopic7
            sub8 = workshop_details.subtopic8
            sub9 = workshop_details.subtopic9
            sub_list = [sub1, sub2, sub3, sub4, sub5, sub6, sub7, sub8, sub9]
            description = workshop_details.description
            rq1 = workshop_details.req1
            rq2 = workshop_details.req2
            rq3 = workshop_details.req3
            rq4 = workshop_details.req4
            rq5 = workshop_details.req5
            rq6 = workshop_details.req6
            rq7 = workshop_details.req7
            rq8 = workshop_details.req8
            rq9 = workshop_details.req9
            req_list = [rq1, rq2, rq3, rq4, rq5, rq6, rq7, rq8, rq9]
            r1 = workshop_details.result1
            r2 = workshop_details.result2
            r3 = workshop_details.result3
            r4 = workshop_details.result4
            r5 = workshop_details.result5
            r6 = workshop_details.result6
            r7 = workshop_details.result7
            r8 = workshop_details.result8
            r9 = workshop_details.result9
            result_list = [r1, r2, r3, r4, r5, r6, r7, r8, r9]
            date = workshop.date
            time = workshop.time
            s2_date = workshop.s2_date
            s3_date = workshop.s3_date
            s4_date = workshop.s4_date
            s2_time = workshop.s2_time
            s3_time = workshop.s3_time
            s4_time = workshop.s4_time

            workshops = db.session.query(Workshop)
            for workshop in workshops:
                if not workshop.reg_start and not workshop.reg_close and workshop.name != ws:
                    upcoming_workshop_list.append(workshop.name)
            upcoming_workshop_list.append(main_ws_on_page.name)
            cover_path = f"../static/images/workshops/{ws}/cover.jpg"

            # ------------------------------------------ INSTRUCTOR ARTWORKS ----------------------------------------- #

            member_id = 1
            teacher = db.session.query(Member).filter_by(id=member_id).one_or_none()
            first_name = teacher.name.split(' ')[0]
            artworks = []
            artworks_dir = f'static/files/users/{first_name}{member_id}/artworks/thumbnail/'
            for entry in os.scandir(artworks_dir):
                if entry.is_file():
                    artworks.append(f'/{artworks_dir}{entry.name}')
            random.shuffle(artworks)

            return render_template('workshops_second.html', category=category, topic=topic, sessions=sessions,
                                   brief=brief,
                                   sub_list=sub_list, description=description, req_list=req_list,
                                   result_list=result_list,
                                   logged_in=current_user.is_authenticated,
                                   upcoming_workshop_list=upcoming_workshop_list, date=date, cover_path=cover_path,
                                   time=time, admin=admin, ws=ws, s2_date=s2_date, s3_date=s3_date, s4_date=s4_date,
                                   s2_time=s2_time, s3_time=s3_time, s4_time=s4_time, artworks=artworks)

    workshops = db.session.query(Workshop)
    reg_status = db.session.query(Tools).filter_by(keyword='reg_status').one().data
    for workshop in workshops:
        if not workshop.reg_start:
            upcoming_workshop_list.append(workshop.name)
    cover_path = f"../static/images/workshops/{current_workshop_name}/cover.jpg"

    # ------------------------------------------------ INSTRUCTOR ARTWORKS ----------------------------------------- #

    member_id = 1
    teacher = db.session.query(Member).filter_by(id=member_id).one_or_none()
    first_name = teacher.name.split(' ')[0]
    artworks = []
    artworks_dir = f'static/files/users/{first_name}{member_id}/artworks/thumbnail/'
    for entry in os.scandir(artworks_dir):
        if entry.is_file():
            artworks.append(f'/{artworks_dir}{entry.name}')
    random.shuffle(artworks)
    return render_template('workshops_main.html', category=category, topic=topic, sessions=sessions, brief=brief,
                           sub_list=sub_list, description=description, req_list=req_list, result_list=result_list,
                           logged_in=current_user.is_authenticated, upcoming_workshop_list=upcoming_workshop_list,
                           date=date, time=time, admin=admin, reg_status=reg_status, cover_path=cover_path,
                           current_workshop_name=current_workshop_name, s2_date=s2_date, s3_date=s3_date,
                           s4_date=s4_date, s2_time=s2_time, s3_time=s3_time, s4_time=s4_time, artworks=artworks)


@school.route('/upcoming_workshop', methods=['GET', 'POST'])
def upcoming_workshop():
    session['url'] = url_for('school.upcoming_workshop')
    upcoming_workshop_list = []
    admin = db.session.query(Role).filter_by(name='admin').first()
    # ---------------------------------------------- INSTRUCTOR ARTWORKS ----------------------------------------- #

    member_id = 1
    teacher = db.session.query(Member).filter_by(id=member_id).one_or_none()
    first_name = teacher.name.split(' ')[0]
    artworks = []
    artworks_dir = f'static/files/users/{first_name}{member_id}/artworks/thumbnail/'
    for entry in os.scandir(artworks_dir):
        if entry.is_file():
            artworks.append(f'/{artworks_dir}{entry.name}')
    random.shuffle(artworks)

    if request.form.get('submit'):
        ws = request.form.get('submit')
        main_ws_on_page = db.session.query(Workshop).filter_by(name=ws).first()
        workshop = db.session.query(Workshop).filter_by(name=ws).first()
        workshop_details = workshop.details

        category = workshop_details.category
        sessions = workshop_details.sessions
        topic = workshop.topic
        brief = workshop_details.brief
        sub1 = workshop_details.subtopic1
        sub2 = workshop_details.subtopic2
        sub3 = workshop_details.subtopic3
        sub4 = workshop_details.subtopic4
        sub5 = workshop_details.subtopic5
        sub6 = workshop_details.subtopic6
        sub7 = workshop_details.subtopic7
        sub8 = workshop_details.subtopic8
        sub9 = workshop_details.subtopic9
        sub_list = [sub1, sub2, sub3, sub4, sub5, sub6, sub7, sub8, sub9]
        description = workshop_details.description
        rq1 = workshop_details.req1
        rq2 = workshop_details.req2
        rq3 = workshop_details.req3
        rq4 = workshop_details.req4
        rq5 = workshop_details.req5
        rq6 = workshop_details.req6
        rq7 = workshop_details.req7
        rq8 = workshop_details.req8
        rq9 = workshop_details.req9
        req_list = [rq1, rq2, rq3, rq4, rq5, rq6, rq7, rq8, rq9]
        r1 = workshop_details.result1
        r2 = workshop_details.result2
        r3 = workshop_details.result3
        r4 = workshop_details.result4
        r5 = workshop_details.result5
        r6 = workshop_details.result6
        r7 = workshop_details.result7
        r8 = workshop_details.result8
        r9 = workshop_details.result9
        result_list = [r1, r2, r3, r4, r5, r6, r7, r8, r9]
        date = workshop.date
        time = workshop.time
        s2_date = workshop.s2_date
        s3_date = workshop.s3_date
        s4_date = workshop.s4_date
        s2_time = workshop.s2_time
        s3_time = workshop.s3_time
        s4_time = workshop.s4_time

        workshops = db.session.query(Workshop)
        for workshop in workshops:
            if not workshop.reg_start and not workshop.reg_close and workshop.name != ws:
                upcoming_workshop_list.append(workshop.name)
        upcoming_workshop_list.append(main_ws_on_page.name)
        cover_path = f"../static/images/workshops/{ws}/cover.jpg"

        return render_template('workshops_second.html', category=category, topic=topic, sessions=sessions,
                               brief=brief,
                               sub_list=sub_list, description=description, req_list=req_list,
                               result_list=result_list,
                               logged_in=current_user.is_authenticated,
                               upcoming_workshop_list=upcoming_workshop_list, date=date, cover_path=cover_path,
                               time=time, admin=admin, ws=ws, s2_date=s2_date, s3_date=s3_date, s4_date=s4_date,
                               s2_time=s2_time, s3_time=s3_time, s4_time=s4_time, artworks=artworks)
    if request.args:
        ws = request.args.get('workshop')
        main_ws_on_page = db.session.query(Workshop).filter_by(name=ws).first()
        workshop = db.session.query(Workshop).filter_by(name=ws).first()
        workshop_details = workshop.details

        category = workshop_details.category
        sessions = workshop_details.sessions
        topic = workshop.topic
        brief = workshop_details.brief
        sub1 = workshop_details.subtopic1
        sub2 = workshop_details.subtopic2
        sub3 = workshop_details.subtopic3
        sub4 = workshop_details.subtopic4
        sub5 = workshop_details.subtopic5
        sub6 = workshop_details.subtopic6
        sub7 = workshop_details.subtopic7
        sub8 = workshop_details.subtopic8
        sub9 = workshop_details.subtopic9
        sub_list = [sub1, sub2, sub3, sub4, sub5, sub6, sub7, sub8, sub9]
        description = workshop_details.description
        rq1 = workshop_details.req1
        rq2 = workshop_details.req2
        rq3 = workshop_details.req3
        rq4 = workshop_details.req4
        rq5 = workshop_details.req5
        rq6 = workshop_details.req6
        rq7 = workshop_details.req7
        rq8 = workshop_details.req8
        rq9 = workshop_details.req9
        req_list = [rq1, rq2, rq3, rq4, rq5, rq6, rq7, rq8, rq9]
        r1 = workshop_details.result1
        r2 = workshop_details.result2
        r3 = workshop_details.result3
        r4 = workshop_details.result4
        r5 = workshop_details.result5
        r6 = workshop_details.result6
        r7 = workshop_details.result7
        r8 = workshop_details.result8
        r9 = workshop_details.result9
        result_list = [r1, r2, r3, r4, r5, r6, r7, r8, r9]
        date = workshop.date
        time = workshop.time
        s2_date = workshop.s2_date
        s3_date = workshop.s3_date
        s4_date = workshop.s4_date
        s2_time = workshop.s2_time
        s3_time = workshop.s3_time
        s4_time = workshop.s4_time

        workshops = db.session.query(Workshop)
        for workshop in workshops:
            if not workshop.reg_start and not workshop.reg_close and workshop.name != ws:
                upcoming_workshop_list.append(workshop.name)
        upcoming_workshop_list.append(main_ws_on_page.name)
        cover_path = f"../static/images/workshops/{ws}/cover.jpg"

        return render_template('workshops_second.html', category=category, topic=topic, sessions=sessions,
                               brief=brief,
                               sub_list=sub_list, description=description, req_list=req_list,
                               result_list=result_list,
                               logged_in=current_user.is_authenticated,
                               upcoming_workshop_list=upcoming_workshop_list, date=date, cover_path=cover_path,
                               time=time, admin=admin, ws=ws, s2_date=s2_date, s3_date=s3_date, s4_date=s4_date,
                               s2_time=s2_time, s3_time=s3_time, s4_time=s4_time, artworks=artworks)
    upcoming_workshop_dict = {}
    workshops = db.session.query(Workshop)
    for workshop in workshops:
        if not workshop.reg_start:
            ws_name = workshop.name
            ws_topic = workshop.topic
            upcoming_workshop_dict[ws_name] = ws_topic
    return render_template('upcoming_workshops.html', upcoming_workshop_dict=upcoming_workshop_dict,
                           logged_in=current_user.is_authenticated)


@school.route('/classroom', methods=['GET', 'POST'])
def classroom():
    session['url'] = url_for('school.classroom')
    admin = db.session.query(Role).filter_by(name='admin').one_or_none()
    all_recorded_video_urls = []
    vid_caption_list = []
    qa_recorded_video_urls = []
    qa_vid_caption_list = []

    workshops = db.session.query(Workshop).all()
    q_a_ws_list = []
    for workshop in workshops:
        if workshop.details.category == 'Q&A':
            q_a_ws_list.append(workshop)

        # if workshop.details.category == 'Q&A':
        #     print('Got the details category qa')
        #     q_a_ws_list.append(workshop)
        # else:
        #     print('skipped category verification')
    q_a_ws_list.reverse()
    all_qa = q_a_ws_list
    for i in all_qa:
        nm = i.name
        topic = i.topic
        vid_list = [i.yt_p1_id, i.yt_p2_id, i.yt_p3_id, i.yt_p4_id]
        for n in range(len(vid_list)):
            if vid_list[n]:
                part = f"Part-{n + 1}"
                caption = f'{nm}-{topic} | {part}'
                qa_recorded_video_urls.append(vid_list[n])
                qa_vid_caption_list.append(caption)
    # print(q_a_ws_list)
    if current_user.is_authenticated:
        ws_list = []

        for ws in current_user.participated:
            if ws.details.category == 'workshop':
                ws_list.append(ws)

        ws_list.reverse()
        all_ws = ws_list
        for i in all_ws:
            nm = i.name
            topic = i.topic
            vid_list = [i.yt_p1_id, i.yt_p2_id, i.yt_p3_id, i.yt_p4_id]
            for n in range(len(vid_list)):
                if vid_list[n]:
                    part = f"Part-{n + 1}"
                    caption = f'{nm}-{topic} | {part}'
                    all_recorded_video_urls.append(vid_list[n])
                    vid_caption_list.append(caption)

    video_count = len(all_recorded_video_urls)
    q_a_video_count = len(qa_recorded_video_urls)

    all_demo_url_list = []
    demo_caption_list = []
    part_list = []
    title_list = []

    result = db.session.query(Demo)
    for r in result:
        url1 = r.vid_id1
        url2 = r.vid_id2
        url3 = r.vid_id3

        if url1 and url1 != '':
            all_demo_url_list.append(url1)
            if url2:
                part_list.append(' | Part 1')
            demo_caption_list.append(r.caption)
            title_list.append(r.title)
        if url2 and url2 != '':
            all_demo_url_list.append(url2)
            part_list.append(' | Part 2')
            demo_caption_list.append(r.caption)
            title_list.append(r.title)
        if url3 and url3 != '':
            all_demo_url_list.append(url3)
            part_list.append(' | Part 3')
            demo_caption_list.append(r.caption)
            title_list.append(r.title)

        demo_caption_list.append(r.caption)

    demo_count = len(all_demo_url_list)
    ws_name_list = []
    ws_dict = {}
    if current_user.is_authenticated:
        enrolled_ws = current_user.participated
        if len(enrolled_ws) >= 0:
            for n in enrolled_ws:
                all_files_path_dict = {}
                base_dir = f"static/files/workshops/{n.name}"
                if not os.path.exists(base_dir):
                    os.makedirs(base_dir)
                folder_content = os.listdir(base_dir)
                for f in folder_content:
                    f_path = base_dir + '/' + f
                    if os.path.isfile(f_path):
                        file_dict = {
                            'file_path': f_path
                        }
                        all_files_path_dict[f] = file_dict

                entry = {
                    "name": n.name,
                    "topic": n.topic,
                    "files": all_files_path_dict
                }
                ws_dict[n.name] = entry
        ws_name_list = list(ws_dict.keys())
    ws_count = len(ws_name_list)

    if request.method == 'POST':
        if request.form.get('download-file'):
            file_path = request.form.get('download-file')
            file_name = request.form.get('file-name')
            ws_name = os.path.basename(os.path.dirname(file_path))
            ws_topic = db.session.query(Workshop).filter_by(name=ws_name).one_or_none().topic
            file_full_name = f'{ws_name}__{ws_topic}__{file_name}'
            with open("download_log.txt", "a") as f:
                f.write(f'{file_full_name} -- downloaded by -- {current_user.name}--{current_user.email}--'
                        f'Id: {current_user.id}---Time: {time_now}\n')
            return send_file(path_or_file=file_path, as_attachment=True, download_name=file_full_name)

    return render_template('classroom.html', vid_id_list=qa_recorded_video_urls, qa_caption_list=qa_vid_caption_list
                           , qa_video_count=q_a_video_count, yt_vid_id_list=all_recorded_video_urls,
                           vid_caption_list=vid_caption_list, video_count=video_count,
                           logged_in=current_user.is_authenticated, admin=admin, all_demo_url_list=all_demo_url_list,
                           demo_caption_list=demo_caption_list, part_list=part_list, demo_count=demo_count,
                           title_list=title_list, ws_dict=ws_dict, ws_name_list=ws_name_list, ws_count=ws_count)


@school.route('/certificate_download', methods=['GET', 'POST'])
def certificate_download():
    if request.method == 'POST':
        if not current_user.is_authenticated:
            session['url'] = url_for('school.certificate_download')
            return redirect(url_for('account.login'))
        if request.form.get('submit') == 'download-cert':
            folder_name = current_user.name.split()[0] + str(current_user.id)
            last_workshop_name = current_user.participated[len(current_user.participated) - 1].name
            topic = current_user.participated[len(current_user.participated) - 1].topic
            file_name = f"{last_workshop_name}-{current_user.name.split()[0]}.jpg"
            path = f"static/files/users/{folder_name}/certificates/{file_name}"
            try:
                return send_file(path_or_file=path, as_attachment=True,
                                 download_name=f"Certificate - {topic} - Writart Gurukul.jpg")
            except Exception as e:
                print(e)
                flash("Oops! There is a problem! No worries! We have informed our tech support team. They'll fix it "
                      "soon!")
                send_email_support(
                    'Error:certificate_download.html',
                    ['shwetabh@writart.com', 'shwetabhartist@gmail.com', 'writart11@gmail.com'],
                    f'Chief! Error while downloading certificate\nUser affected: {current_user}',
                    '', ''
                )
                return redirect(request.url)
    return render_template('certificate_download.html', logged_in=current_user.is_authenticated)


@school.route('/instructor')
def instructor():
    return render_template('instructor.html')


@school.route('/vision')
def vision():
    return render_template('vision.html')


@school.route('/t&c_school')
def terms_and_conditions_school():
    return render_template('t&c_school.html')


