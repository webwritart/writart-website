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
    category = db.Column(db.String(500)) # eg. Print or Original, or recreat select tag in form to collect predefined options
    all_sizes = db.Column(db.String(500)) # sizes separated by '$' in this single column
    all_materials = db.Column(db.String(500)) # materials like canvas, paper etc
    material_charge = db.Column(db.String(500)) # size_price$size2_price2 price to be added in the main price
    media = db.Column(db.String(500)) # material like oil or acrylic or multiple materials separated by '$'
    print_selling_price = db.Column(db.String(500)) # Multiple prices for multiple sizes: size1_price1$size2_price2
    print_discount_percentage = db.Column(db.String(5)) # Multiple discount percentage for different sizes: size1_discountpercent$size2_discountpercent
    original_price = db.Column(db.String(500)) # Price for the original physical artwork
    original_discount_percentage = db.Column(db.String(5))
    recreation_price = db.Column(db.String(500)) # Multiple prices for multiple sizes: size1_price1$size2_price2
    recreation_discount_percentage = db.Column(db.String(500)) # Multiple discount percentage for different sizes: size1_discountpercent$size2_discountpercent
    inventory = db.Column(db.String(500)) #Total remaining items count in case of print size_count$size2_count2
    delivery_charge = db.Column(db.String(500)) # size_price$size2_price2
    recreation = db.Column(db.String(200)) # Recreation option like limited, no, yes etc
    urgent_charge_percentage = db.Column(db.String(500)) # Charge added to base charge based on deadline days eg. days_percentage$days2_percentage2
    original_available = db.Column(db.String(200)) # Original availability yes or no
    delivered_as = db.Column(db.String(500)) # eg. Rolled or stretched
    creation_year = db.Column(db.String(10))
    quality = db.Column(db.String(500))
    shipping = db.Column(db.String(500))
    main_photo_path = db.Column(db.String(500))
    additional_photo_paths = db.Column(db.String(1000)) # paths separated by '$$__$$'
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'))
    approval_status = db.Column(db.String(100))
    features = db.Column(db.String(500)) # Features like 'Writart Choice'

    def __repr__(self):
        return f"{self.uuid}--{self.title}--{self.member_id}--{self.category}"

