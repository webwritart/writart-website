from extensions import db


class Query(db.Model):
    __tablename__ = 'query'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    whatsapp = db.Column(db.String(100))
    phone = db.Column(db.String(100))
    interested_ws = db.Column(db.String(100))
    message = db.Column(db.String(300))




    def __repr__(self):
        return f'{self.name}'
