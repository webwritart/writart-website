from extensions import db


class Query(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    whatsapp = db.Column(db.String(100))
    phone = db.Column(db.String(100))
    interested_ws = db.Column(db.String(100))




    def __repr__(self):
        return f'{self.name}'
