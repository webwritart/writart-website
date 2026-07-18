from extensions import db


class ArtistData(db.Model):
    __tablename__ = 'aritst_data'

    id = db.Column(db.Integer, primary_key=True)
    artist = db.Column(db.String(100))
    watermarked_artworks = db.Column(db.Integer)
    gallery_artworks = db.Column(db.Integer)
    all_collections = db.Column(db.Integer)
    commission_collections = db.Column(db.Integer)
    sold_artworks = db.Column(db.Integer)
    queried_artworks = db.Column(db.Integer)
    shipped_artworks = db.Column(db.Integer)
    contracted_artworks = db.Column(db.Integer)
    sold_commissions = db.Column(db.Integer)
    memory_occupied_total = db.Column(db.Integer)
    memory_occupied_gallery = db.Column(db.Integer)
    member_id = db.Column(db.Integer,db.ForeignKey('member.id'), unique=True)

    def __repr__(self):
        return f"{self.artist}"


class Coa(db.Model):
    __tablename__ = 'coa'

    id = db.Column(db.Integer, primary_key=True)
    serial_no = db.Column(db.String(50), unique=True)
    title = db.Column(db.String(100))
    artist_name = db.Column(db.String(100))
    size = db.Column(db.String(50))
    medium = db.Column(db.String(50))
    varnished = db.Column(db.String(50))
    year = db.Column(db.String(50))
    signed = db.Column(db.String(50))
    statement = db.Column(db.String(50))
    copyright = db.Column(db.String(50))
    client_name = db.Column(db.String(100))
    issue_date = db.Column(db.String(15))
    artist_id = db.Column(db.Integer, db.ForeignKey('member.id'))
    client_id = db.Column(db.Integer, db.ForeignKey('member.id'))

    artist = db.relationship('Member', foreign_keys=[artist_id], back_populates='given_coas')
    client = db.relationship('Member', foreign_keys=[client_id], back_populates='taken_coas')

    def __repr__(self):
        return f"{self.artist_name}--{self.client_name}--{self.serial_no}"
