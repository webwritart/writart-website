import table as table


from extensions import db
from flask_login import UserMixin

member_workshop = db.Table('member_workshop',
                           db.Column('member_id', db.Integer, db.ForeignKey('member.id')),
                           db.Column('workshop_id', db.Integer, db.ForeignKey('workshop.id'))
                           )

member_role = db.Table('member_role',
                       db.Column('member_id', db.Integer, db.ForeignKey('member.id')),
                       db.Column('role_id', db.Integer, db.ForeignKey('role.id'))
                       )


class Member(UserMixin, db.Model):
    __tablename__ = "member"

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
    website = db.Column(db.String(100))
    registration_date = db.Column(db.String(50))
    participated = db.relationship('Workshop', secondary=member_workshop, backref='participants')
    role = db.relationship('Role', secondary=member_role, backref='members')
    demo = db.relationship('Demo', backref='creator')




    def __repr__(self):
        return f'{self.name}, {self.email}, {self.phone}'


class Workshop(db.Model):
    __tablename__ = 'workshop'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(10))
    topic = db.Column(db.String(100))
    date = db.Column(db.String(50))
    time = db.Column(db.String(50))
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
    __tablename__ = 'role'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.String(500))




    def __repr__(self):
        return f'{self.name}'
