from extensions import db


class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(500))
    option_a = db.Column(db.String(200))
    option_b = db.Column(db.String(200))
    option_c = db.Column(db.String(200))
    option_d = db.Column(db.String(200))
    option_e = db.Column(db.String(200))
    answer = db.Column(db.String(1))
    category = db.Column(db.String(50))
    subcategory = db.Column(db.String(50))
    level = db.Column(db.String(30))
    time_played = db.Column(db.Integer)
    time_correct = db.Column(db.Integer)

    def __repr__(self):
        return f'{self.question} -- {self.answer}'
