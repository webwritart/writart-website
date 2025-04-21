import pprint
from flask import jsonify
from app import app
from extensions import db
from models.member import Member, Role, Workshop
from models.query import Query
from models.tool import Tools
from models.workshop_details import WorkshopDetails
from models.payment import Payment
import pandas as pd
from flask_login import login_required, current_user
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


# with app.app_context():


