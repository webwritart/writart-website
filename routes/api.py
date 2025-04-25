import pprint
from flask import Blueprint, render_template, request, jsonify
from models.member import Member, Workshop
from models.query import Query
from models.payment import Payment
from extensions import db
from models.tool import Tools

api_page = Blueprint('api', __name__, static_folder='static', template_folder='templates/api')


@api_page.route('/', methods=['GET', 'POST'])
def api():
    authentication_token = 'grghrh74th**hfrgUFUgeg8430h(*h349(hHGr84('

    client_token = request.args.get('token')
    data = request.args.get('data')
    all_members = db.session.query(Member).all()
    all_interested = db.session.query(Query).all()
    all_workshops = db.session.query(Workshop).all()

    members = {}
    all_students_and_interested = {}
    all_enrolled = {}
    all_interested_dict = {}
    workshops = {}

    all_members_phone = []
    all_interested_phone = []

    def payments_by_quarter(end_month_name, year):
        quarter_payments = {}
        all_payments = db.session.query(Payment).all()

        for payment in all_payments:
            payment_year = payment.date.split('-')[0]
            month = payment.date.split('-')[1]

            if payment_year == year:
                if end_month_name == 'march':
                    if month == '01' or month == '02' or month == '03':
                        invoice = {
                            'id': payment.id,
                            'name': payment.name,
                            'state': payment.state,
                            'amount': payment.amount,
                            'date': payment.date
                        }
                        quarter_payments[payment.id] = invoice
                elif end_month_name == 'june':
                    if month == '04' or month == '05' or month == '06':
                        invoice = {
                            'id': payment.id,
                            'name': payment.name,
                            'state': payment.state,
                            'amount': payment.amount,
                            'date': payment.date
                        }
                        quarter_payments[payment.id] = invoice
                elif end_month_name == 'september':
                    if month == '07' or month == '08' or month == '09':
                        invoice = {
                            'id': payment.id,
                            'name': payment.name,
                            'state': payment.state,
                            'amount': payment.amount,
                            'date': payment.date
                        }
                        quarter_payments[payment.id] = invoice
                elif end_month_name == 'december':
                    if month == '10' or month == '11' or month == '12':
                        print(month)
                        invoice = {
                            'id': payment.id,
                            'name': payment.name,
                            'state': payment.state,
                            'amount': payment.amount,
                            'date': payment.date
                        }
                        quarter_payments[payment.id] = invoice
        return quarter_payments

    def all_enrolled_current_workshop():
        current_ws_name = db.session.query(Tools).filter_by(keyword='current_workshop').one_or_none().data
        current_ws_enrolled = db.session.query(Workshop).filter_by(name=current_ws_name).one_or_none().participants
        current_ws_enrolled_students = {}

        for st in current_ws_enrolled:
            es = {
                'id': st.id,
                'name': st.name,
                'email': st.email,
                'phone': st.phone,
                'whatsapp': st.whatsapp,
            }
            current_ws_enrolled_students[st.id] = es
        return current_ws_enrolled_students

    for m in all_members:
        all_members_phone.append(m.phone)
        member_dict = {
            'id': m.id,
            'name': m.name,
            'email': m.email,
            'phone': m.phone,
            'whatsapp': m.whatsapp,
        }
        members[m.id] = member_dict
        all_students_and_interested[m.id] = member_dict

    for i in all_interested:
        if i.phone not in all_interested_phone:
            all_interested_phone.append(i.phone)
            interested_dict = {
                'id': i.id,
                'name': i.name,
                'email': i.email,
                'whatsapp': i.whatsapp,
                'phone': i.phone,
            }
            all_interested_dict[i.id] = interested_dict
            if i.phone not in all_members_phone:
                all_students_and_interested[i.id] = interested_dict

    for a in all_members:
        if a.participated:
            enrolled = {
                'id': a.id,
                'name': a.name,
                'email': a.email,
                'phone': a.phone,
                'whatsapp': a.whatsapp
            }
            all_enrolled[a.id] = enrolled

    for w in all_workshops:
        students = w.participants
        enrolled_phone_list = []
        enrolled_list = []
        interested_list = []
        all_list = []
        for s in students:
            enrolled_phone_list.append(s.phone)
            student = {
                'id': s.id,
                'name': s.name,
                'email': s.email,
                'whatsapp': s.whatsapp,
                'phone': s.phone
            }
            enrolled_list.append(student)
            all_list.append(student)
        for i in all_interested:
            if i.interested_ws == w.name:
                interested = {
                    'id': i.id,
                    'name': i.name,
                    'email': i.email,
                    'whatsapp': i.whatsapp,
                    'phone': i.phone
                }
                interested_list.append(interested)
                if i.phone not in enrolled_phone_list:
                    all_list.append(interested)
        workshop_dict = {
            'id': w.id,
            'name': w.name,
            'topic': w.topic,
            'date': w.date,
            'time': w.time,
            'instructor': w.instructor,
            'strength': w.strength,
            'gross_revenue': w.gross_revenue,
            'joining_link': w.joining_link,
            'joining_link2': w.joining_link2,
            'joining_link3': w.joining_link3,
            'joining_link4': w.joining_link4,
            'yt_p1_id': w.yt_p1_id,
            'yt_p2_id': w.yt_p2_id,
            'yt_p3_id': w.yt_p3_id,
            'yt_p4_id': w.yt_p4_id,
            'reg_start': w.reg_start,
            'reg_close': w.reg_close,
            'enrolled_students': enrolled_list,
            'interested_students': interested_list,
            'all_students': all_list
        }
        workshops[w.id] = workshop_dict

    if client_token == authentication_token:
        if data == 'members':
            return jsonify(members)
        elif data == 'interested':
            return jsonify(all_interested_dict)
        elif data == 'members_interested':
            return jsonify(all_students_and_interested)
        elif data == 'enrolled':
            return jsonify(all_enrolled)
        elif data == 'workshops':
            return jsonify(workshops)
        elif data == 'payments':
            end_month_name = request.args.get('end_month_name')
            year = request.args.get('year')
            return jsonify(payments_by_quarter(end_month_name, year))
        elif data == 'current_ws_enrolled':
            return jsonify(all_enrolled_current_workshop())
        else:
            return jsonify('Wrong data type!')
    else:
        return jsonify('Authentication error!')
