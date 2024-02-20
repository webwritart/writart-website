from extensions import db


class ArtistData(db.Model):

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


