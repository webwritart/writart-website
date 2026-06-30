import os
from pprint import pprint
import random
from flask import Blueprint, render_template, request, redirect, flash, send_file, session, url_for, jsonify
from flask_login import current_user
from werkzeug.utils import secure_filename
from extensions import db, current_year,p
from pathlib import Path
from models.query import Query
from models.tool import Tools
from models.member import Workshop, Role, Member, QuizList, FeedbackCredits, FeedbackVideos, WorkshopAssignmentAssessmentVideos, WorkshopDemo
from models.videos import Demo
from models.quiz import Quiz
from models.workshop_details import WorkshopDetails
from operations.messenger import *
import webbrowser
from datetime import datetime, date, timedelta

time_now = datetime.now()

school = Blueprint('school', __name__, static_folder='static', template_folder='templates/school')


@school.route('/', methods=['GET', 'POST'])
def home():
   return render_template('school.html', logged_in=current_user.is_authenticated)

@school.route('/workshops', methods=['GET', 'POST'])
def workshops():
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
            artworks = []
            try:
                member_id = 1
                teacher = db.session.query(Member).filter_by(id=member_id).one_or_none()
                first_name = teacher.name.split(' ')[0]
                artworks_dir = f'static/files/users/{first_name}{member_id}/artworks/thumbnail/'
                for entry in os.scandir(artworks_dir):
                    if entry.is_file():
                        artworks.append(f'/{artworks_dir}{entry.name}')
                random.shuffle(artworks)
            except Exception as e:
                print(e)

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
    artworks = []

    try:
        member_id = 1
        teacher = db.session.query(Member).filter_by(id=member_id).one_or_none()
        first_name = teacher.name.split(' ')[0]
        artworks_dir = f'static/files/users/{first_name}{member_id}/artworks/thumbnail/'
        for entry in os.scandir(artworks_dir):
            if entry.is_file():
                artworks.append(f'/{artworks_dir}{entry.name}')
        random.shuffle(artworks)
    except Exception as e:
        print(e)

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
    role = ''
    session['url'] = url_for('school.classroom')
    p(session.get('url'))
    admin = db.session.query(Role).filter_by(name='admin').one_or_none()
    if current_user.is_authenticated:
        if admin in current_user.role:
            role = 'admin'
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
    ws_dict = {}
    

    if request.method == 'POST':
        if request.form.get('download-file'):
            file_path = request.form.get('download-file')
            p(file_path)
            file_name = request.form.get('file-name')
            ws_uuid = file_path.split('/')[-3]
            p(ws_uuid)
            ws_topic = db.session.query(Workshop).filter_by(uuid=ws_uuid).one_or_none().topic
            file_full_name = f'{ws_topic}__{file_name}'
            with open("download_log.txt", "a") as f:
                f.write(f'{file_full_name} -- downloaded by -- {current_user.name}--{current_user.email}--'
                        f'Id: {current_user.id}---Time: {time_now}\n')
            return send_file(path_or_file=file_path, as_attachment=True, download_name=file_full_name)
# ---------------------------------------- Course/Workshop Thumbnails --------------------------------------------- #
    workshop_name_thumbnail_dict = {}
    ws_thumbnail_base_url = "../static/images/courses/"
    workshop_list = db.session.query(Workshop).all()
    for workshop in workshop_list:
        uuid = workshop.uuid
        name = workshop.name
        category = workshop.details.category
        if category != 'Q&A':
            thumbnail = f'{ws_thumbnail_base_url}{uuid}/thumbnail.jpg'
            workshop_name_thumbnail_dict[name] = {'name':name,
                                                  'uuid':uuid,
                                                  'thumbnail_url':thumbnail}
    workshop_count = len(workshop_name_thumbnail_dict)
    workshop_name_thumbnail_dict = dict(reversed(workshop_name_thumbnail_dict.items()))



# ------------------------------------------------------- QUIZ ---------------------------------------------------------------------- #
    result = db.session.query(Quiz).all()
    questions = {}
    category_list = []
    for r in result:
        q_id = r.id
        q = r.question
        oa = r.option_a.strip()
        ob = r.option_b.strip()
        oc = r.option_c.strip()
        od = r.option_d.strip()
        oe = r.option_e.strip()
        ans = r.answer
        cat = r.category
        subcat = r.subcategory
        level = r.level
        t_played = r.time_played
        t_correct = r.time_correct
        answer = ''
        if oa[0] == ans:
            answer = oa
        elif ob[0] == ans:
            answer = ob
        elif oc[0] == ans:
            answer = oc
        elif od[0] == ans:
            answer = od
        elif oe[0] == oe:
            answer = oe

        if cat not in category_list:
            category_list.append(cat)
        entry = {
            'q': q,
            'oa': oa,
            'ob': ob,
            'oc': oc,
            'od': od,
            'oe': oe,
            'ans': ans,
            'answer': answer,
            'cat': cat,
            'subcat': subcat,
            'level': level,
            't_played': t_played,
            't_correct': t_correct
        }
        questions[q_id] = entry
    date_today = date.today()    

    return render_template('classroom.html', vid_id_list=qa_recorded_video_urls, qa_caption_list=qa_vid_caption_list
                           , qa_video_count=q_a_video_count, yt_vid_id_list=all_recorded_video_urls,
                           vid_caption_list=vid_caption_list, workshop_count=workshop_count,
                           logged_in=current_user.is_authenticated, admin=admin, all_demo_url_list=all_demo_url_list,
                           demo_caption_list=demo_caption_list, part_list=part_list, demo_count=demo_count,
                           title_list=title_list, ws_dict=ws_dict,
                           questions=questions, category_list=category_list,role=role,
                           ws_thumbnail_dict=workshop_name_thumbnail_dict)


@school.route('/course', methods=['GET','POST'])
def course():
    if current_user.is_authenticated:
        if 'ws_uuid' in session or request.args.get('ws_uuid'):
            vid_id_list = []
            vid_caption_list = []
            
            if request.args.get('ws_uuid'):
                ws_uuid = request.args.get('ws_uuid')
                session['ws_uuid'] = request.args.get('ws_uuid')

            else:
                ws_uuid = session.get('ws_uuid')
            
            ws_id = db.session.query(Workshop).filter_by(uuid=ws_uuid).scalar().id
            
            workshop = db.session.query(Workshop).filter_by(uuid=ws_uuid).scalar()
            category = workshop.details.category
            ws_topic = workshop.topic

            if category == 'course':
                videos_row_list = workshop.videos
                for video in videos_row_list:
                    vid_id = video.vid_id
                    vid_id_list.append(vid_id)
                    vid_caption = video.title
                    vid_caption_list.append(vid_caption)
            else:
                if category != 'Q&A':
                    topic = workshop.topic
                    vid_list = [workshop.yt_p1_id, workshop.yt_p2_id, workshop.yt_p3_id, workshop.yt_p4_id]
                    for n in range(len(vid_list)):
                        if vid_list[n]:
                            part = f"Part-{n + 1}"
                            caption = f'{topic} | {part}'
                            vid_id_list.append(vid_list[n])
                            vid_caption_list.append(caption)
                else:
                    print(workshop.details.category)

            video_count = len(vid_id_list)

    # ----------------------------------- ASSESSMENT VIDEOS ---------------------------------------------------#
            assessment_vid_dict = {}
            all_assessed_videos = db.session.query(WorkshopAssignmentAssessmentVideos).filter_by(ws_id=ws_id).all()
            for v in all_assessed_videos:
                assessment_vid_dict[v.vid_caption] = {
                    'vid_id': v.yt_vid_id,
                    'vid_caption': v.vid_caption
                }
            assessment_video_count = len(assessment_vid_dict)
            

    # -------------------------------------- DEMO VIDEOS ------------------------------------------------------ #
            demo_vid_dict = {}
            all_demo_videos = db.session.query(WorkshopDemo).filter_by(ws_id=ws_id).all()
            for v in all_demo_videos:
                demo_vid_dict[v.vid_caption] = {
                    'vid_id': v.yt_vid_id,
                    'vid_caption': v.vid_caption
                }
            demo_video_count = len(demo_vid_dict)

            # ------------------------------ STUDY MATERIAL ----------------------------------------------- #
            study_material_dict = {}
            base_dir = f"static/files/courses/{ws_uuid}/notes"
            if not os.path.exists(base_dir):
                os.makedirs(base_dir)
            folder_content = os.listdir(base_dir)
            for f in folder_content:
                f_path = base_dir + '/' + f
                if os.path.isfile(f_path):
                    material = {
                        'file_path': f_path
                    }
                    study_material_dict[f] = material
            study_material_count = len(study_material_dict)

            # ----------------------------------- ASSIGNMENTS ---------------------------------------------- #
            assignments_dict = {}
            base_dir = f"static/files/courses/{ws_uuid}/assignments"
            if not os.path.exists(base_dir):
                os.makedirs(base_dir)
            folder_content = os.listdir(base_dir)
            for f in folder_content:
                f_path = base_dir + '/' + f
                if os.path.isfile(f_path):
                    assignment = {
                        'file_path': f_path
                    }
                    assignments_dict[f] = assignment
            assignments_count = len(assignments_dict)
            assignments_dict = dict(sorted(assignments_dict.items()))

            # ------------------------------- ASSIGNMENTS SUBMISSION ------------------------------------------ #
            if request.method == 'POST':
                if request.form.get('submit') == 'submit_assignments':
                    files = request.files.getlist('assignments')
                    file_count = len(files)
                    ws_uuid = session.get('ws_uuid')
                    student_uuid = current_user.uuid
                    student_name = current_user.name

                    folder = f'./static/files/courses/{ws_uuid}/assignment-submissions/'
                    if not os.path.exists(folder):
                        os.makedirs(folder)
                    
                    for file in files:
                        if file.filename == '':
                            flash('No selected file', 'error')
                            return redirect(request.url)
                        else:
                            filename = secure_filename(file.filename)
                            file_name = f"{ws_uuid}_{student_uuid}_{student_name}_{filename}"
                            file.save(f"{folder}{file_name}")
                    date_time = datetime.now().replace(microsecond=0)
                    subject = f"ASSIGNMENT SUBMISSION - {date_time}"
                    total_assignment_count = len(os.listdir(folder)) - 1
                    body = f"{file_count} assignments submitted by {current_user.name}.\nTotal submissions: {total_assignment_count}"
                    send_email_school(subject, ['shwetabhartist@gmail.com', 'writartstudios@gmail.com'], body, '', '')
                    flash("Images uploaded successfully!", "success")
                    return redirect(url_for('school.course') + '#submit-assignments')
            # -------------------------------------------------------------------------------------------------- #
            
            ws_credit_dict = {}
            total_ws_credits = 0
            all_workshop_with_credit = []
            total_topic_credits = 0
            feedback_topics_data = db.session.query(Tools).filter_by(keyword='artwork_feedback_topics').scalar().data
            feedback_topic_list = feedback_topics_data.split('/')
            try:
                result = db.session.query(FeedbackCredits).filter_by(student_id=current_user.id, category='workshop').all()
                for r in result:
                    if r.credits > 0:
                        all_workshop_with_credit.append(r.workshop_id)
                for a in all_workshop_with_credit:
                    workshop_topic = db.session.query(Workshop).filter_by(id=a).scalar().topic
                    feedback_credit = db.session.query(FeedbackCredits).filter_by(workshop_id=a).scalar()
                    w_credits = feedback_credit.credits
                    total_ws_credits += int(w_credits)
                    credit_date = feedback_credit.date
                    date_object = datetime.strptime(credit_date, '%Y-%m-%d')
                    expiry_date_obj = date_object + timedelta(days=30)
                    expiry_date = expiry_date_obj.strftime('%Y-%m-%d')
                    entry = {
                        'title': workshop_topic,
                        'credits': w_credits,
                        'expiry': expiry_date
                    }
                    ws_credit_dict[a] = entry
            except Exception as e:
                print(e)

            no_ws_credit_dict = len(ws_credit_dict)
            total_ws_credits = ''
            try:
                total_topic_credits = db.session.query(FeedbackCredits).filter_by(student_id=current_user.id, category='topic').scalar().credits
            except Exception as e:
                print(e)
        else:
            return redirect(url_for('school.classroom'))
    else:
        return redirect(url_for('school.classroom'))

    return render_template('course.html', logged_in=current_user.is_authenticated,
                           video_count=video_count, vid_id_list=vid_id_list, vid_caption_list=vid_caption_list,
                           ws_topic=ws_topic, study_material_dict=study_material_dict, study_material_count=study_material_count,
                           assignments_dict=assignments_dict, assignments_count=assignments_count, no_ws_credit_dict=no_ws_credit_dict,
                           total_topic_credits=total_topic_credits, ws_uuid=ws_uuid,
                           ws_credit_dict=ws_credit_dict, total_ws_credits=total_ws_credits,
                           feedback_topic_list=feedback_topic_list, assessment_vid_dict=assessment_vid_dict, assessment_video_count=assessment_video_count,
                           demo_vid_dict=demo_vid_dict, demo_video_count=demo_video_count)


@school.route('/submit-feedback-files', methods=['GET', 'POST'])
def submit_feedback_files():
    # -------------------------------------------- TEACHER'S FEEDBACK ------------------------------------------------- #

    if request.method == 'POST':
        # if request.form.get('submit-topic-feedback') == 'Submit Artworks':
        #     if 'ws-feedback-files' not in request.files:
        #         flash('No file part', 'error')
        #         return redirect(request.url)
        #     files = request.files.getlist('ws-feedback-files')
        #     no_submitted_files = len(files)

        #     
        #     # ----------------------------------------------------------------------------------- #

        #     folder = f'static/files/users/{current_user.uuid}/teacher_feedback/pending/'
        #     if not os.path.exists(folder):
        #         os.makedirs(folder)

        #     for file in files:
        #         if file.filename == '':
        #             flash('No selected file', 'error')
        #             return redirect(request.url)
        #         filename_base = secure_filename(file.filename)
        #         filename =f"{feedback_uuid}$${filename_base}" 
        #         # file.save(os.path.join(folder, filename))

                

        #     # deduct total credits ----------------------------------------------------------------------
            
        #     return redirect(url_for('school.course', _anchor='ws-feedback-form'))
        
        if request.form.get('submit-topic-feedback') == 'Submit Artworks':
            all_feedback_uuid_list = []

            topic = request.form.get('topic')
            if 'topic-feedback-files' not in request.files:
                flash('No file part', 'error')
                return redirect(request.url)
            files = request.files.getlist('topic-feedback-files')
            no_files = len(files)
            folder = f'static/files/users/{current_user.uuid}/teacher-feedbacks/pending/'
            if not os.path.exists(folder):
                os.makedirs(folder)
            for file in files:
            # -------------------------------------- CREATE FEEDBACK UUID ----------------------------- #
                try:
                    all_feedbacks = db.session.query(FeedbackVideos).all()
                    for f in all_feedbacks:
                        all_feedback_uuid_list.append(f.uuid)
                except Exception as e:
                    p(e)
                
                feedback_uuid = ''
                process_continue = True
                while process_continue:
                    feedback_uuid = random.randint(10000000, 99999999)
                    if feedback_uuid not in all_feedback_uuid_list:
                        process_continue = False
            # ------------------------------------------------------------------------------------------ #
                if file.filename == '':
                    flash('No selected file', 'error')
                    return redirect(request.url)
                filename_base = secure_filename(file.filename)
                filename = f"{feedback_uuid}$${filename_base}"
                file.save(os.path.join(folder, filename))

                date_today = date.today()
                entry = FeedbackVideos(
                    yt_vid_id='',
                    date=date_today,
                    member_uuid=current_user.uuid,
                    topic=topic,
                    instructor='Shwetabh Suman',
                    uuid=feedback_uuid,
                    status='pending',
                    artwork_title=filename_base
                )
                db.session.add(entry)
                db.session.commit()
            flash('Successfully Submitted', 'success')
            p('submitted')
            return redirect(url_for('school.course', ws_uuid=session.get('ws_uuid')))
    return redirect(url_for('school.course'), ws_uuid=session.get('ws_uuid'))


@school.route('/save-quiz-data', methods=['POST'])
def save_quiz_data():
    if request.is_json:
        data = request.get_json()
        correct = data['correct']
        current_q_id = data['current_q_id']
        time_played = db.session.query(Quiz).filter_by(id=current_q_id).one_or_none().time_played
        time_correct = db.session.query(Quiz).filter_by(id=current_q_id).one_or_none().time_correct
        time_p = time_played+1
        time_c = time_correct+correct
        db.session.query(Quiz).filter_by(id=current_q_id).one_or_none().time_played = time_p
        db.session.query(Quiz).filter_by(id=current_q_id).one_or_none().time_correct = time_c
        db.session.commit()
        return jsonify('success!')


@school.route('/save-member-quiz-data', methods=['POST'])
def save_member_quiz_data():
    if current_user.is_authenticated:
        if request.is_json:
            data = request.get_json()
            cat = data['category']
            total = data['total']
            total_correct = data['total_correct']
            date_today = date.today()

            entry = QuizList(
                category=cat,
                correct=total_correct,
                total=total,
                date_played=date_today,
                player_id=current_user.id
            )
            db.session.add(entry)
            db.session.commit()
            return jsonify('success!')
    else:
        return jsonify('User not logged in!')


@school.route('/certificate_download', methods=['GET', 'POST'])
def certificate_download():
    admin = db.session.query(Role).filter_by(name='admin').scalar()
    if not current_user.is_authenticated:
        return redirect(url_for('account.login', instruction='Pleae Log in First'))
    else:
        certificate_dict = {}

        user_uuid = current_user.uuid
        folder = f"./static/files/users/{user_uuid}/certificates"
        if not os.path.exists(folder):
            os.makedirs(folder)
        all_files = os.listdir(folder)
        for file in all_files:
            file_path = Path(folder + '/' + file)
            if file_path.is_file():
                course_uuid = file.split('.')[0].split('_')[1]
                course_topic = db.session.query(Workshop).filter_by(uuid=course_uuid).scalar().topic
                certificate_dict[course_topic] = {
                    'course_topic': course_topic,
                    'certificate_path': file_path
                }

        if request.method == 'POST':
            if not current_user.is_authenticated:
                session['url'] = url_for('school.certificate_download')
                return redirect(url_for('account.login'))
            else:
                download_path = request.form.get('submit').split('|')[0]
                file_default_name = Path(download_path).name
                extension = file_default_name.split('.')[1]
                topic = request.form.get('submit').split('|')[1]

                file_name = f"Certificate_{topic}_writart-studio.{extension}"

                try:
                    return send_file(path_or_file=download_path, as_attachment=True,
                                    download_name=file_name)
                except Exception as e:
                    print(e)
                    flash("Oops! There is a problem! No worries! We have informed our tech support team. They'll fix it "
                        "soon!")
                    send_email_support(
                        'Error:certificate_download.html',
                        ['shwetabhartist@gmail.com', 'writartstudios@gmail.com'],
                        f'Chief! Error while downloading certificate\nUser affected: {current_user}',
                        '', ''
                    )
                    return redirect(request.url)
    return render_template('certificate_download.html', logged_in=current_user.is_authenticated, admin=admin, current_year=current_year,
                           certificate_dict=certificate_dict)


@school.route('/instructor')
def instructor():
    return render_template('instructor.html')


@school.route('/vision')
def vision():
    return render_template('vision.html')


@school.route('/t&c_school')
def terms_and_conditions_school():
    return render_template('t&c_school.html')


