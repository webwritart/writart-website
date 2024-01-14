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
    participated = db.relationship('Workshop', secondary=user_workshop, backref='participants')
    role = db.relationship('Role', secondary=user_role, backref='members')



    def __repr__(self):
        return f'{self.name}, {self.email}, {self.phone}'


class Workshop(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(10))
    topic = db.Column(db.String(100))
    date = db.Column(db.String(50))
    instructor = db.Column(db.String(100))
    strength = db.Column(db.String(50))
    gross_revenue = db.Column(db.String(100))
    joining_link = db.Column(db.String(100))
    joining_link2 = db.Column(db.String(100))
    joining_link3 = db.Column(db.String(100))
    joining_link4 = db.Column(db.String(100))
    yt_p1_id = db.Column(db.String(100))
    yt_p2_id = db.Column(db.String(100))
    yt_p3_id = db.Column(db.String(100))
    yt_p4_id = db.Column(db.String(100))
    reg_start = db.Column(db.String(50))
    reg_close = db.Column(db.String(50))
    details = db.relationship('WorkshopDetails', backref='workshop', uselist=False)




    def __repr__(self):
        return f'{self.name}, {self.topic}, {self.date}'


class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.String(500))




    def __repr__(self):
        return f'{self.name}'
