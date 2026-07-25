from extensions import db


class Artwork(db.Model):
    __tablename__ = "artwork"

    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.Integer, unique=True)
    title = db.Column(db.String(200))
    product_title = db.Column(db.String(500))
    theme = db.Column(db.String(500))
    short_description = db.Column(db.String(400))
    long_description = db.Column(db.String(1000))
    net_rating = db.Column(db.String(10))
    medium = db.Column(db.String(500)) # material like oil or acrylic or multiple materials separated by '$'
    surface = db.Column(db.String(500)) # eg. paper, canvas, board
    original_size = db.Column(db.String(200))
    original_price = db.Column(db.String(500)) # Price for the original physical artwork
    original_discount_percentage = db.Column(db.String(5))
    print = db.Column(db.String(200)) # Print option like yes, no or limited etc.
    limited_print_count = db.Column(db.Integer)
    print_size_list = db.Column(db.String(500)) # list of sizes eg. [A1, A2, '4 x 6 inch']
    recreation = db.Column(db.String(200)) # Recreation option like limited, no, yes etc
    limited_recreation_count = db.Column(db.Integer)
    recreation_media_list = db.Column(db.String(500)) # list of recreation media eb. ['oil']
    original_available = db.Column(db.String(200)) # Original availability yes or no
    creation_year = db.Column(db.String(10))
    main_photo_path = db.Column(db.String(500))
    additional_photo_paths = db.Column(db.String(1000)) # paths as list
    hd_photo_path = db.Column(db.String(500)) # Path for photo used for prints
    approval_status = db.Column(db.String(100))
    features = db.Column(db.String(500)) # Features like 'Writart Choice'
    date_time_uploaded = db.Column(db.String(100))
    sale_status = db.Column(db.String(100)) # Only applicable for original artwork eg. sold, available
    art_name = db.Column(db.String(200)) # pseudo name of the artist, Optional
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'))
    variants = db.relationship('ArtworkVariants', backref='artwork')

    def __repr__(self):
        return f"{self.uuid}--{self.title}--{self.member_id}"


class ArtworkVariants(db.Model):
    __tablename__ = "artwork_variants"

    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(200)) # eg. print or recreation
    subcategory = db.Column(db.String(200)) # eg. photo or canvas for print category
    medium = db.Column(db.String(200))
    surface = db.Column(db.String(200))
    size = db.Column(db.String(200))
    price = db.Column(db.Integer)
    discount_percent = db.Column(db.Integer)
    inventory = db.Column(db.Integer)
    delivery_charge = db.Column(db.Integer)
    urgent_charge_percentage = db.Column(db.Integer)
    delivered_as = db.Column(db.String(500)) # eg. Rolled or stretched
    artwork_id = db.Column(db.Integer, db.ForeignKey('artwork.id'))

    def __repr__(self):
        return f"{self.category}--{self.subcategory}--{self.size}--{self.price}"



