class Tools(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    keyword = db.Column(db.String(100))
    data = db.Column(db.String(100))




    def __repr__(self):
        return f'{self.keyword}'