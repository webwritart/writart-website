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