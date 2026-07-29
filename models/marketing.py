from extensions import db


class NewsLetterList(db.Model):
    __tablename__ = 'newsletter_list'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(200))
    segment = db.Column(db.String(100))
    sub_segment = db.Column(db.String(100))
    description = db.Column(db.String(500))
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'))

    def __repr__(self):
        return f"email: {self.email}-- segment: {self.segment}"