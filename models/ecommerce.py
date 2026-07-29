from extensions import db


class Payment(db.Model):
    __tablename__ = 'payment'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    state = db.Column(db.String(100))
    amount = db.Column(db.String(50))
    message = db.Column(db.String(500))
    ws_name = db.Column(db.String(100))
    date = db.Column(db.String(50))
    order_id = db.Column(db.String(100))
    payment_id = db.Column(db.String(100))
    invoice_no = db.Column(db.String(50))

    def __repr__(self):
        return f'{self.name}, {self.amount}, {self.ws_name}'

class CartItem(db.Model):
    __tablename__ = 'cart_item'

    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.Integer, unique=True) # 8 digit
    quantity = db.Column(db.Integer, nullable=False)
    added_at_price = db.Column(db.Integer, nullable=False)
    attributes = db.Column(db.String(500)) # Stores custom text engravings, gift wraps, or ad-hoc custom details.
    created_at = db.Column(db.String(100)) # Date and time of cart addition
    updated_at = db.Column(db.String(100)) # Date and time of cart updation
    product_id = db.Column(db.Integer, db.ForeignKey('artwork.id'), nullable=False)
    variant_id = db.Column(db.Integer, db.ForeignKey('artwork_variants.id'), nullable=False, unique=True)
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'), nullable=False)

    def __repr__(self):
        return f"Member id: {self.member_id}-- Product id: {self.product_id}-- Created at: {self.created_at}"
