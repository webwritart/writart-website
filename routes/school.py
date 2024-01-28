from flask import Blueprint, render_template, request, redirect, flash
from flask_login import current_user
from extensions import db
from models.query import Query
from models.tool import Tools
from models.member import Workshop, Role
from models.workshop_details import WorkshopDetails

school = Blueprint('school', __name__, static_folder='static', template_folder='templates')


@school.route('/', methods=['GET', 'POST'])
def home():
    upcoming_workshop_list = []
    admin = db.session.query(Role).filter_by(name='admin').first()
    if request.method == 'POST':
        if request.form.get('interested-form-hidden-workshop2'):
            ws_name = request.form.get('interested-form-hidden-workshop2')
            try:
                name = current_user.name
                email = current_user.email
                phone = current_user.phone
                whatsapp = current_user.whatsapp
            except:
                name = request.form.get('name')
                email = request.form.get('email')
                phone = request.form.get('phone')
                whatsapp = request.form.get('whatsapp')
            message = request.form.get('message')

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

        if request.form.get('interested-form-hidden-workshop'):
            ws_name = request.form.get('interested-form-hidden-workshop')
            try:
                name = current_user.name
                email = current_user.email
                phone = current_user.phone
                whatsapp = current_user.whatsapp
            except:
                name = request.form.get('name')
                email = request.form.get('email')
                phone = request.form.get('phone')
                whatsapp = request.form.get('whatsapp')
            message = request.form.get('message')

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

        if request.form.get('know-more') == 'know-more':
            ws = request.form.get('submit')
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

            workshops = db.session.query(Workshop)
            for workshop in workshops:
                if not workshop.reg_start and workshop.name != ws:
                    upcoming_workshop_list.append(workshop.name)

            return render_template('workshops_second.html', category=category, topic=topic, sessions=sessions,
                                   brief=brief,
                                   sub_list=sub_list, description=description, req_list=req_list,
                                   result_list=result_list,
                                   logged_in=current_user.is_authenticated,
                                   upcoming_workshop_list=upcoming_workshop_list, date=date, time=time, admin=admin,
                                   ws=ws)

    current_workshop_name = db.session.query(Tools).filter_by(keyword='current_workshop').first().data
    current_workshop = db.session.query(Workshop).filter_by(name=current_workshop_name).first()
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

    upcoming_workshop_list = []
    workshops = db.session.query(Workshop)
    reg_status = db.session.query(Tools).filter_by(keyword='reg_status').one()
    for workshop in workshops:
        if not workshop.reg_start:
            upcoming_workshop_list.append(workshop.name)
    return render_template('workshops_main.html', category=category, topic=topic, sessions=sessions, brief=brief,
                           sub_list=sub_list, description=description, req_list=req_list, result_list=result_list,
                           logged_in=current_user.is_authenticated, upcoming_workshop_list=upcoming_workshop_list,
                           date=date, time=time, admin=admin, reg_status=reg_status)


@school.route('/classroom')
def classroom():
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

    return render_template('classroom.html', vid_id_list=qa_recorded_video_urls, qa_caption_list=qa_vid_caption_list
                           , qa_video_count=q_a_video_count, yt_vid_id_list=all_recorded_video_urls,
                           vid_caption_list=vid_caption_list, video_count=video_count,
                           logged_in=current_user.is_authenticated, admin=admin)
