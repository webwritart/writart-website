import pprint

from app import app
from extensions import db
from models.member import Member, Role, Workshop
from models.query import Query
from models.tool import Tools
from models.workshop_details import WorkshopDetails
import pandas as pd
from flask_login import login_required, current_user
from operations.messenger import send_wa_msg_by_list
from urllib.parse import quote
from datetime import datetime,timezone
import pytz

# df = pd.read_csv('role.csv')
# df = df.reset_index()
# with app.app_context():
#     for index, row in df.iterrows():
#         name = row['name']
#         description = row['description']
#
#         entry = Role(
#             name=name,
#             description=description
#         )
#         db.session.add(entry)
#
#     db.session.commit()
#     print('Hoorey! Transfer accomplished successfully!')

# with app.app_context():
#     user = db.session.query(Member).filter_by(id=2).one()
#     ws1 = db.session.query(Workshop).filter_by(id=1).one()
#     ws2 = db.session.query(Workshop).filter_by(id=2).one()
#     ws3 = db.session.query(Workshop).filter_by(id=3).one()
#
#     user.participated.append(ws1)
#     user.participated.append(ws2)
#     user.participated.append(ws3)
#
#     db.session.commit()


# num_list = ['918920351265', '918920351265']
# name_list = ['Shwetabh', 'Shwetabh']
# wa_msg = f"Dear [name],\nClass has begun!\nPlease hop in!\nlink: https://writart.com"
# # send_wa_msg_by_list(wa_msg, num_list, name_list)
# indiatz = pytz.timezone("Asia/Kolkata")
# now = datetime.now(indiatz)
# with open('operations/wa_log.txt', 'a') as the_file:
#     the_file.write(f'{now} --- Failed to send message to number\n')
with app.app_context():
    all_workshops = db.session.query(Workshop).all()
    all_interested = db.session.query(Query).all()
    all_workshops_dict = {}
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
        all_workshops_dict[w.id] = workshop_dict

pprint.pprint(all_workshops_dict)
