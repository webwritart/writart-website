from extensions import db


class Demo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    caption = db.Column(db.String(500))
    vid_id1 = db.Column(db.String(100))
    vid_id2 = db.Column(db.String(100))
    vid_id3 = db.Column(db.String(100))
    tags = db.Column(db.String(500))
    date = db.Column(db.String(100))
    level = db.Column(db.String(100))
    creator_id = db.Column(db.Integer, db.ForeignKey('member.id'))




    def __repr__(self):
        return f"Title: {self.title}, Creator: {self.creator}"
