from extensions import db


class WorkshopDetails(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(100))
    brief = db.Column(db.String(100))
    sessions = db.Column(db.String(2))
    subtopic1 = db.Column(db.String(100))
    subtopic2 = db.Column(db.String(100))
    subtopic3 = db.Column(db.String(100))
    subtopic4 = db.Column(db.String(100))
    subtopic5 = db.Column(db.String(100))
    subtopic6 = db.Column(db.String(100))
    subtopic7 = db.Column(db.String(100))
    subtopic8 = db.Column(db.String(100))
    subtopic9 = db.Column(db.String(100))
    description = db.Column(db.String(500))
    req1 = db.Column(db.String(100))
    req2 = db.Column(db.String(100))
    req3 = db.Column(db.String(100))
    req4 = db.Column(db.String(100))
    req5 = db.Column(db.String(100))
    req6 = db.Column(db.String(100))
    req7 = db.Column(db.String(100))
    req8 = db.Column(db.String(100))
    req9 = db.Column(db.String(100))
    result1 = db.Column(db.String(100))
    result2 = db.Column(db.String(100))
    result3 = db.Column(db.String(100))
    result4 = db.Column(db.String(100))
    result5 = db.Column(db.String(100))
    result6 = db.Column(db.String(100))
    result7 = db.Column(db.String(100))
    result8 = db.Column(db.String(100))
    result9 = db.Column(db.String(100))
    cover = db.Column(db.String(100))
    thumbnail = db.Column(db.String(100))
    photo1 = db.Column(db.String(100))
    photo2 = db.Column(db.String(100))
    photo3 = db.Column(db.String(100))
    ws_id = db.Column(db.Integer, db.ForeignKey('workshop.id'), unique=True)




    def __repr__(self):
        return f'Details of: {self.category}'