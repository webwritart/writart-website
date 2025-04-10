from app import app
from extensions import db
from models.member import Member, Role, Workshop
from models.tool import Tools
from models.workshop_details import WorkshopDetails
import pandas as pd

# df = pd.read_csv('workshop_details.csv')
# df = df.reset_index()
# with app.app_context():
#     for index, row in df.iterrows():
#         category = row['category']
#         brief = row['brief']
#         sessions = row['sessions']
#         subtopic1 = row['subtopic1']
#         subtopic2 = row['subtopic2']
#         subtopic3 = row['subtopic3']
#         subtopic4 = row['subtopic4']
#         subtopic5 = row['subtopic5']
#         subtopic6 = row['subtopic6']
#         subtopic7 = row['subtopic7']
#         subtopic8 = row['subtopic8']
#         subtopic9 = row['subtopic9']
#         description = row['description']
#         req1 = row['req1']
#         req2 = row['req2']
#         req3 = row['req3']
#         req4 = row['req4']
#         req5 = row['req5']
#         req6 = row['req6']
#         req7 = row['req7']
#         req8 = row['req8']
#         req9 = row['req9']
#         result1 = row['result1']
#         result2 = row['result2']
#         result3 = row['result3']
#         result4 = row['result4']
#         result5 = row['result5']
#         result6 = row['result6']
#         result7 = row['result7']
#         result8 = row['result8']
#         result9 = row['result9']
#         cover = row['cover']
#         thumbnail = row['thumbnail']
#         photo1 = row['photo1']
#         photo2 = row['photo2']
#         photo3 = row['photo3']
#         ws_id = row['ws_id']
#
#         entry = WorkshopDetails(
#             category=category,
#             brief=brief,
#             sessions=sessions,
#             subtopic1=subtopic1,
#             subtopic2=subtopic2,
#             subtopic3=subtopic3,
#             subtopic4=subtopic4,
#             subtopic5=subtopic5,
#             subtopic6=subtopic6,
#             subtopic7=subtopic7,
#             subtopic8=subtopic8,
#             subtopic9=subtopic9,
#             description=description,
#             req1=req1,
#             req2=req2,
#             req3=req3,
#             req4=req4,
#             req5=req5,
#             req6=req6,
#             req7=req7,
#             req8=req8,
#             req9=req9,
#             result1=result1,
#             result2=result2,
#             result3=result3,
#             result4=result4,
#             result5=result5,
#             result6=result6,
#             result7=result7,
#             result8=result8,
#             result9=result9,
#             cover=cover,
#             thumbnail=thumbnail,
#             photo1=photo1,
#             photo2=photo2,
#             photo3=photo3,
#             ws_id=ws_id
#         )
#         db.session.add(entry)
#
#     db.session.commit()
#     print('Hoorey! Transfer accomplished successfully!')