from extensions import db


class Tools(db.Model):
    __tablename__ = 'tools'

    id = db.Column(db.Integer, primary_key=True)
    keyword = db.Column(db.String(100))
    data = db.Column(db.String(100))

    def __repr__(self):
        return f'{self.keyword}'


class ArtworkPriceTime(db.Model):
    __tablename__ = 'artwork_price_time'

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50))
    price = db.Column(db.Integer)
    discount_percentage = db.Column(db.Integer)
    time_taken = db.Column(db.String(50))

    def __repr__(self):
        return f'{self.type}'