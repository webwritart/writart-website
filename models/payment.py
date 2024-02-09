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