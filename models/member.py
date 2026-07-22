# import table as table
from sqlalchemy.sql.operators import truediv

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

member_project = db.Table('member_project',
                          db.Column('member_id', db.Integer, db.ForeignKey('member.id')),
                          db.Column('project_id', db.Integer, db.ForeignKey('project.id'))
                          )

member_workshop_month = db.Table('member_workshop_month',
                                 db.Column('member_id', db.Integer, db.ForeignKey('member.id')),
                                 db.Column('workshop_month_id', db.Integer, db.ForeignKey('workshop_month.id'))
                                 )


class Member(UserMixin, db.Model):
    __tablename__ = "member"

    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.Integer, unique=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
    phone = db.Column(db.String(15), unique=True)
    whatsapp = db.Column(db.String(15))
    profession = db.Column(db.String(100))
    sex = db.Column(db.String(10))
    dob = db.Column(db.String(15))
    billing_address = db.Column(db.String(500))
    billing_state = db.Column(db.String(100))
    billing_country = db.Column(db.String(100))
    billing_pincode = db.Column(db.String(20))
    shipping_address = db.Column(db.String(500))
    shipping_state = db.Column(db.String(100))
    shipping_country = db.Column(db.String(100))
    shipping_pincode = db.Column(db.String(20))
    website = db.Column(db.String(100))
    fb_url = db.Column(db.String(100))
    insta_url = db.Column(db.String(100))
    x = db.Column(db.String(100))
    registration_date = db.Column(db.String(50))
    token = db.Column(db.String(10))
    participated = db.relationship('Workshop', secondary=member_workshop, backref='participants')
    role = db.relationship('Role', secondary=member_role, backref='members')
    ws_months = db.relationship('WorkshopMonth', secondary=member_workshop_month, backref='members')
    demo = db.relationship('Demo', backref='creator')
    artist_data = db.relationship('ArtistData', backref='member', uselist=False)
    project = db.relationship('Project', secondary=member_project, backref='clients')
    quizzes = db.relationship('QuizList', backref='player')
    tickets = db.relationship('SupportTicket', backref='member')
    feedback_credits = db.relationship('FeedbackCredits', backref='student')
    portraits = db.relationship('Portrait', backref='artist')
    certificates = db.relationship('Certificate', backref='member')
    invoices = db.relationship('Invoice', backref='member')
    given_coas = db.relationship('Coa', foreign_keys='Coa.artist_id', back_populates='artist')
    taken_coas = db.relationship('Coa', foreign_keys='Coa.client_id', back_populates='client')


    def __repr__(self):
        return f'{self.name.split()[0]} -- {self.email}'



class Certificate(db.Model):
    __tablename__ = 'certificate'

    id = db.Column(db.Integer, primary_key=True)
    certificate_no = db.Column(db.String(50), unique=True)
    awardee_name = db.Column(db.String(100))
    course_topic = db.Column(db.String(100))
    course_uuid = db.Column(db.String(10))
    course_period = db.Column(db.String(50))
    session_type = db.Column(db.String(50))
    instructor = db.Column(db.String(100))
    lead_instructor = db.Column(db.String(100))
    issue_date = db.Column(db.String(50))
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'))

    def __repr__(self):
        return f'{self.course_topic}, Certificate No. {self.certificate_no}'




class Portrait(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(6), unique=True)
    title = db.Column(db.String(100))
    description = db.Column(db.String(500))
    medium = db.Column(db.String(100))
    artist_name = db.Column(db.String(100))
    date_time = db.Column(db.String(50))
    path = db.Column(db.String(200))
    artist_id = db.Column(db.Integer, db.ForeignKey('member.id'))


    def __repr__(self):
        return f"{self.title}"



class QuizList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(255))
    correct = db.Column(db.Integer)
    total = db.Column(db.Integer)
    date_played = db.Column(db.String(10))
    player_id = db.Column(db.Integer, db.ForeignKey('member.id'))

    def __repr__(self):
        return f'player_id: {self.player_id}, Correct: {self.correct}, Total: {self.total}'


class FeedbackCredits(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    workshop_id = db.Column(db.Integer, unique=True)
    category = db.Column(db.String(100))
    credits = db.Column(db.Integer)
    date = db.Column(db.String(15))
    student_id = db.Column(db.Integer, db.ForeignKey('member.id'))

    def __repr__(self):
        return f'Member id: {self.student_id}, Category: {self.category}, Workshop id: {self.workshop_id}, Date: {self.date}'


class FeedbackVideos(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    yt_vid_id = db.Column(db.String(100))
    date = db.Column(db.String(15))
    member_uuid = db.Column(db.Integer)
    topic = db.Column(db.String(100))
    instructor = db.Column(db.String(100))
    uuid = db.Column(db.Integer, unique=True)
    status = db.Column(db.String(50))
    exists = db.Column(db.Boolean, default=True, nullable=False)
    artwork_title = db.Column(db.String(100))

    def __repr__(self):
        return f'Title: {self.yt_vid_id}, Date: {self.date}'


class Workshop(db.Model):
    __tablename__ = 'workshop'

    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.Integer, unique=True)
    name = db.Column(db.String(100))
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
    s2_date = db.Column(db.String(100))
    s2_time = db.Column(db.String(100))
    s3_date = db.Column(db.String(100))
    s3_time = db.Column(db.String(100))
    s4_date = db.Column(db.String(100))
    s4_time = db.Column(db.String(100))
    months = db.relationship('WorkshopMonth', backref='workshop')
    details = db.relationship('WorkshopDetails', backref='workshop', uselist=False)
    videos = db.relationship('WorkshopVideos', backref='workshop')
    assignment_assessment_videos = db.relationship('WorkshopAssignmentAssessmentVideos', backref='workshop')

    def __repr__(self):
        return f'{self.name}, {self.topic}'
    

class WorkshopMonth(db.Model):
    __tablename__ = 'workshop_month'
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.Integer, unique=True)
    month = db.Column(db.Integer)
    title = db.Column(db.String(50))
    detail = db.Column(db.String(100))
    workshop_id = db.Column(db.Integer, db.ForeignKey('workshop.id'))
    videos = db.relationship('MonthVideos', backref='month')
    notes = db.relationship('MonthNotes', backref='month')
    assignments = db.relationship('MonthAssignments', backref='month')
    assignment_assessment_videos = db.relationship('MonthAssignmentAssessmentVideos', backref='month')
    demos = db.relationship('MonthDemo', backref='month')


def __repr__(self):
    return f'{self.workshop_id} - {self.month} month'


class MonthVideos(db.Model):
    __tablename__ = 'month_videos'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    vid_id = db.Column(db.String(100))
    detail = db.Column(db.String(200))
    date_time = db.Column(db.String(50))
    month_id = db.Column(db.Integer, db.ForeignKey('workshop_month.id'))

    def __repr__(self):
        return f'{self.title}'
    
    
class MonthNotes(db.Model):
    __tablename__ = 'month_notes'
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.Integer, unique=True)
    file_name = db.Column(db.String(50))
    date_time = db.Column(db.String(50))
    month_id = db.Column(db.Integer, db.ForeignKey('workshop_month.id'))

    def __repr__(self):
        return f'{self.file_name}'
    
    
class MonthAssignments(db.Model):
    __tablename__ = 'month_assignments'
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.Integer, unique=True)
    file_name = db.Column(db.String(50))
    date_time = db.Column(db.String(50))
    month_id = db.Column(db.Integer, db.ForeignKey('workshop_month.id'))

    def __repr__(self):
        return f'{self.file_name}'
    

class MonthAssignmentAssessmentVideos(db.Model):
    __tablename__ = 'month_assignment_assessment_videos'
    id = db.Column(db.Integer, primary_key=True)
    yt_vid_id = db.Column(db.String(100))
    vid_caption = db.Column(db.String(100))
    instructor = db.Column(db.String(100))
    date_time = db.Column(db.String(50))
    month_id = db.Column(db.Integer, db.ForeignKey('workshop_month.id'))

    def __repr__(self):
        return f'{self.vid_caption}'
    

class MonthDemo(db.Model):
    __tablename__ = 'month_demo'
    id = db.Column(db.Integer, primary_key=True)
    yt_vid_id = db.Column(db.String(100))
    vid_caption = db.Column(db.String(100))
    instructor = db.Column(db.String(100))
    date_time = db.Column(db.String(50))
    month_id = db.Column(db.Integer, db.ForeignKey('workshop_month.id'))

    def __repr__(self):
        return f'{self.vid_caption}'


class WorkshopVideos(db.Model):
    __tablename__ = 'workshop_videos'
    id = db.Column(db.Integer, primary_key=True)
    ws_name = db.Column(db.String(100))
    title = db.Column(db.String(100))
    vid_id = db.Column(db.String(100))
    workshop_id = db.Column(db.Integer, db.ForeignKey('workshop.id'))

    def __repr__(self):
        return f'{self.title}'



class WorkshopAssignmentAssessmentVideos(db.Model):
    __tablename__ = 'workshop_assignment_assessment_videos'
    id = db.Column(db.Integer, primary_key=True)
    ws_id = db.Column(db.Integer, db.ForeignKey('workshop.id'))
    yt_vid_id = db.Column(db.String(100))
    vid_caption = db.Column(db.String(100))
    instructor = db.Column(db.String(100))
    date_time = db.Column(db.String(50))

    def __repr__(self):
        return f"{self.ws_id}-{self.vid_caption}-{self.instructor}"
    

class WorkshopDemo(db.Model):
    __tablename__ = 'workshop_demo'
    id = db.Column(db.Integer, primary_key=True)
    ws_id = db.Column(db.Integer, db.ForeignKey('workshop.id'))
    yt_vid_id = db.Column(db.String(100))
    vid_caption = db.Column(db.String(100))
    instructor = db.Column(db.String(100))
    date_time = db.Column(db.String(50))

    def __repr__(self):
        return f"{self.ws_id}-{self.vid_caption}-{self.instructor}"
        


class Role(db.Model):
    __tablename__ = 'role'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.String(500))

    def __repr__(self):
        return f'{self.name}'


class Project(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    category = db.Column(db.String(50))
    short_description = db.Column(db.String(200))
    detailed_description = db.Column(db.String(1000))
    start_date = db.Column(db.String(12))
    deadline = db.Column(db.String(12))
    sponsors = db.Column(db.String(5000))
    producers = db.Column(db.String(5000))

    def __repr__(self):
        return f'{self.name}'

