from extensions import db
from flask_login import UserMixin


user_workshop = db.Table('user_workshop',
                         db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                         db.Column('workshop_id', db.Integer, db.ForeignKey('workshop.id'))
                         )

user_role = db.Table('user_role',
                     db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                     db.Column('role_id', db.Integer, db.ForeignKey('role.id'))
                     )

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
    phone = db.Column(db.String(15), unique=True)
    whatsapp = db.Column(db.String(15))
    profession = db.Column(db.String(100))
    sex = db.Column(db.String(10))
    dob = db.Column(db.String(15))
    state = db.Column(db.String(100))
    fb_url = db.Column(db.String(100))
    insta_url = db.Column(db.String(100))
    website = db.Column(db.String(100))
    registration_date = db.Column(db.String(50))
    participated = db.relationship('workshop.Workshop', secondary="user_workshop", backref='participants')
    role = db.relationship('role.Role', secondary="user_role", backref='members')




    def __repr__(self):
        return f'{self.name}, {self.email}, {self.phone}'
