from extensions import db


class News(db.Model):
    __tablename__ = 'news'

    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50))
    text = db.Column(db.String(100))
    link = db.Column(db.String(50))
    date_time = db.Column(db.String(20))

    def __repr__(self):
        return f'{self.category}\n{self.text}'
