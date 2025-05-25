from extensions import db


class VidEditProject(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    models = db.Column(db.String(20))
    animation = db.Column(db.String(20))
    cut = db.Column(db.String(20))
    edit = db.Column(db.String(20))
    vfx = db.Column(db.String(20))
    color = db.Column(db.String(20))
    audio = db.Column(db.String(20))


    def __repr__(self):
        return f'{self.name}'

