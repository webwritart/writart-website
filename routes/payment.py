from flask import Blueprint, render_template, request, current_app, redirect, url_for
from flask_login import current_user
from extensions import db, image_dict

from datetime import date
import razorpay
import os
from messenger import send_email_support
from models.payment import Payment
from models.tool import Tools
from models.user import *


payment = Blueprint('payment', __name__, static_folder='static', template_folder='templates')


KEY_ID = os.environ.get('RAZORPAY_KEY_ID_TEST')
KEY_SECRET = os.environ.get('RAZORPAY_KEY_SECRET_TEST')
client = razorpay.Client(auth=(KEY_ID, KEY_SECRET))

today_date = date.today()


@payment.route('/')
def home():
    global current_ws, current_ws_name, current_ws_topic, student
    current_ws_name = db.session.query(Tools).filter_by(keyword='current_workshop').one().data
    current_ws = db.session.query(Workshop).filter_by(name=current_ws_name).one()
    current_ws_topic = current_ws.topic
    student = db.session.query(Role).filter_by(name='student').one()
    return render_template('order.html', logged_in=current_user.is_authenticated)


@payment.route('/checkout', methods=['POST'])
def checkout():
    # current_ws_name = db.session.query(Workshop)[db.session.query(Workshop).count()-1].name
    global payment, msg
    name = current_user.name
    email = current_user.email
    phone = current_user.phone
    amt = request.form.get('amount')
    amount = f"{amt}00"
    msg = request.form.get('message')

    data = {"amount": amount, "currency": "INR", "receipt": "#105"}
    payment = client.order.create(data=data)

    return render_template('checkout.html', payment=payment, name=name, email=email, phone=phone, key_id=KEY_ID,
                           ws_name=current_ws_name, logged_in=current_user.is_authenticated)


@payment.route('/verify', methods=['POST'])
def verify():
    global payment, msg
    resp = request.get_data()
    response = resp.decode('utf-8').split('&')
    response_data = {
        "razorpay_payment_id": response[0].split('=')[1],
        "razorpay_order_id": response[1].split('=')[1],
        "razorpay_signature": response[2].split('=')[1]
    }
    amount = payment['amount']
    order_id = payment['id']

    if client.utility.verify_payment_signature(response_data):
        client.payment.capture(response_data["razorpay_payment_id"], amount)
        month = str(today_date).split('-')[1]
        year = str(today_date).split('-')[0]
        inv_n = db.session.query(Tools).filter_by(keyword='last invoice').one().data
        if len(inv_n) == 1:
            inv_no = f"00{inv_n}"
        elif len(inv_n) == 2:
            inv_no = f"0{inv_n}"
        else:
            inv_no = inv_n
        invoice = f"INV-{year}-{month}-{inv_no}"
        if current_user.whatsapp:
            phone = current_user.whatsapp
        else:
            phone = current_user.phone
        entry = Payment(
            name=current_user.name,
            email=current_user.email,
            phone=phone,
            state=current_user.state,
            amount=str(payment['amount'])[:-2],
            message=msg,
            order_id=order_id,
            invoice_no=invoice,
            payment_id=response[0].split('=')[1],
            date=today_date,
            ws_name=current_ws_name
        )
        db.session.add(entry)
        if inv_n == '999':
            db.session.query(Tools).filter_by(keyword='last invoice').one().data = '1'
        else:
            db.session.query(Tools).filter_by(keyword='last invoice').one().data = str(int(inv_no) + 1)
        db.session.commit()
        topic = current_ws_topic
        date_time = current_ws.date
        session_link = current_ws.joining_link
        mail = render_template('mails/enrollment_success.html', topic=topic, date_time=date_time,session_link=session_link)

        try:
            current_user.role.append(student)
            db.session.commit()
        except:
            pass
        try:
            current_user.participated.append(current_ws)
            db.session.commit()
        except:
            pass
        try:
            send_email_support('Enrolled', [current_user.email],
                               '',
                               mail,
                               image_dict)
        except:
            pass
        return redirect(url_for('payment.ws_registration_success'))

    return render_template('order.html', logged_in=current_user.is_authenticated)


@payment.route('/ws_registration_success')
def ws_registration_success():
    return render_template('ws_registration_success.html', logged_in=current_user.is_authenticated)