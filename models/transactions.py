from extensions import db


class Invoice(db.Model):
    __tablename__ = 'invoice'

    id = db.Column(db.Integer, primary_key=True)
    invoice_no = db.Column(db.String(12), unique=True)
    name = db.Column(db.String(100))
    address = db.Column(db.String(200))
    state = db.Column(db.String(50))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(50))
    items_name = db.Column(db.String(500))
    items_price = db.Column(db.String(500))
    items_quantity = db.Column(db.String(200))
    tax_percent = db.Column(db.String(100))
    sub_total = db.Column(db.String(100))
    grand_total = db.Column(db.String(100))
    status = db.Column(db.String(20))
    receipt_no = db.Column(db.String(20))
    date_time = db.Column(db.String(30))
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'))

    def __repr__(self):
        return f'{self.invoice_no}--{self.name}--{self.grand_total}'
    

class Receipt(db.Model):
    __tablename__ = 'receipt'

    id = db.Column(db.Integer, primary_key=True)
    receipt_no = db.Column(db.String(12), unique=True)
    name = db.Column(db.String(100))
    address = db.Column(db.String(200))
    state = db.Column(db.String(50))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(50))
    items_name = db.Column(db.String(500))
    items_price = db.Column(db.String(500))
    items_quantity = db.Column(db.String(200))
    tax_percent = db.Column(db.String(100))
    sub_total = db.Column(db.String(100))
    grand_total = db.Column(db.String(100))
    payment_type = db.Column(db.String(10))
    amount_paid = db.Column(db.String(50))
    invoice_no = db.Column(db.String(20))
    date_time = db.Column(db.String(30))
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'))

    def __repr__(self):
        return f'{self.receipt_no}--{self.name}--{self.grand_total}'