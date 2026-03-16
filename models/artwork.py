from extensions import db


class Portrait(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(6), unique=True)
    title = db.Column(db.String(100))
    description = db.Column(db.String(500))
    medium = db.Column(db.String(100))
    artist = db.Column(db.String(100))
    path = db.Column(db.String(200))


    def __repr__(self):
        return f"{self.title}"