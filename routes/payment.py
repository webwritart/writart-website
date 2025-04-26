import csv
import pprint
import hmac
import hashlib
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from flask_login import current_user, login_required
from extensions import image_dict, current_year
from dotenv import load_dotenv
from datetime import date
import razorpay
import os
from operations.messenger import send_email_support
from models.payment import Payment
from models.tool import Tools
from models.member import *
from datetime import datetime

now = datetime.now()

load_dotenv()

payment = Blueprint('payment', __name__, static_folder='static', template_folder='templates/payment')

KEY_ID = os.environ.get('RAZORPAY_KEY_ID_LIVE')
KEY_SECRET = os.environ.get('RAZORPAY_KEY_SECRET_LIVE')

client = razorpay.Client(auth=(KEY_ID, KEY_SECRET))

today_date = date.today()
payment_ = {}


@login_required
@payment.route('/')
def home():
    session['url'] = url_for('payment.home')
    global current_ws, current_ws_name, current_ws_topic, student
    # return render_template('maintenance.html')

    try:
        if current_user.name:
            current_ws_name = db.session.query(Tools).filter_by(keyword='current_workshop').one().data
            current_ws = db.session.query(Workshop).filter_by(name=current_ws_name).one()
            current_ws_topic = current_ws.topic
            student = db.session.query(Role).filter_by(name='student').one()
            return render_template('order.html', logged_in=current_user.is_authenticated)
    except Exception as e:
        instruction = 'Please first login to enroll'
        return render_template('account/login.html', prev_page='enroll', instruction=instruction)


@login_required
@payment.route('/checkout', methods=['POST'])
def checkout():
    global payment_, msg
    current_ws_name = db.session.query(Tools).filter_by(keyword='current_workshop').first().data
    current_workshop = db.session.query(Workshop).filter_by(name=current_ws_name).one_or_none()
    name = current_user.name
    email = current_user.email
    phone = current_user.phone
    state = request.form.get('state')
    amt = request.form.get('amount')
    amount = int(f"{amt}00")
    msg = request.form.get('message')
    session['msg'] = msg
    if current_workshop not in current_user.participated:
        data = {"amount": amount, "currency": "INR", "receipt": "#105", "notes": [state]}
        session['payment_data'] = client.order.create(data=data)
        order_id = session['payment_data']['id']
        return render_template('checkout.html', order_id=order_id, name=name, email=email, phone=phone, key_id=KEY_ID,
                               ws_name=current_ws_name, state=state, logged_in=current_user.is_authenticated)
    else:
        flash("You have already enrolled to this program!", "error")
        return redirect(url_for('payment.home'))


@login_required
@payment.route('/verify', methods=['POST'])
def verify():
    resp = request.get_data()
    response = resp.decode('utf-8').split('&')
    amount = session['payment_data']['amount']
    amount_paid = session['payment_data']['amount_paid']
    order_id = session['payment_data']['id']
    state = session['payment_data']['notes'][0]
    current_workshop_name = db.session.query(Tools).filter_by(keyword='current_workshop').one_or_none().data
    current_ws = db.session.query(Workshop).filter_by(name=current_workshop_name).one_or_none()

    response_data = {
        "razorpay_payment_id": response[0].split('=')[1],
        "razorpay_order_id": response[1].split('=')[1],
        "razorpay_signature": response[2].split('=')[1]
    }
    parameters = {
        "razorpay_order_id": order_id,
        "razorpay_payment_id": response[0].split('=')[1],
        "razorpay_signature": response[2].split('=')[1]
    }
    # msg = "{}|{}".format(order_id, response_data["razorpay_payment_id"])
    # secret = KEY_SECRET
    # body = bytes(msg, 'utf-8')
    # key = bytes(secret, 'utf-8')
    # dig = hmac.new(key=key, msg=body, digestmod=hashlib.sha256)
    # generated_signature = dig.hexdigest()
    # signature = response_data["razorpay_signature"]
    # print(f'Generated_signature: {generated_signature}')
    # print(f'signature: {signature}')

    # result = hmac.compare_digest(generated_signature, signature)
    # if result:
    #     print("signature verified successfully!")
    # if client.utility.verify_payment_signature(parameters):
    # client.payment.capture(response_data["razorpay_payment_id"], amount)
    if resp:
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
            state=state,
            amount=str(amount)[:-2],
            message=session['msg'],
            order_id=order_id,
            invoice_no=invoice,
            payment_id=response[0].split('=')[1],
            date=today_date,
            ws_name=current_workshop_name
        )
        db.session.add(entry)
        if inv_n == '999':
            db.session.query(Tools).filter_by(keyword='last invoice').one().data = '1'
        else:
            db.session.query(Tools).filter_by(keyword='last invoice').one().data = str(int(inv_no) + 1)
        db.session.commit()
        file_path = "log.txt"
        f = open(file_path, "a")
        f.write(f'Added Payment! - {now}\n')
        f.close()
        current_workshop = db.session.query(Workshop).filter_by(name=current_workshop_name).one_or_none()
        topic = db.session.query(Workshop).filter_by(name=current_workshop_name).one_or_none().topic
        dt = current_workshop.date
        time = current_workshop.time
        date_time = f'{dt} ({time})'
        session_link = current_ws.joining_link
        mail = render_template('mails/enrollment_success.html', topic=topic, date_time=date_time,
                               session_link=session_link)
        f = open(file_path, "a")
        f.write(f'Mailed! - {now}\n')
        f.close()

        try:
            current_user.role.append(student)
            db.session.commit()
            f = open(file_path, "a")
            f.write(f'Assigned student role! - {now}\n')
            f.close()
        except Exception as e:
            pass
        try:
            current_user.participated.append(current_ws)
            db.session.commit()
            f = open(file_path, "a")
            f.write(f'Enrolled! - {now}\n')
            f.close()
        except Exception as e:
            pass
        try:
            send_email_support('Enrolled', [current_user.email],
                               '',
                               mail,
                               '')
            mail_body = f"Dear Chief\n\nNew enrollment! Hooray!\n\nDetails:\nname: {current_user.name}\n" \
                        f"Email: {current_user.email}\nPhone: {current_user.phone}\nState: {state}\nAmount: {str(amount)[:-2]}\n" \
                        f"Message: {session['msg']}\nWorkshop: {current_workshop_name}\n\n"
            send_email_support('New Enrollment', ['writartstudios@gmail.com'], mail_body, '', '')
            f = open(file_path, "a")
            f.write(f'sent mail again! - {now}\n')
            f.close()
        except Exception as e:
            pass
        return redirect(url_for('payment.ws_registration_success'))
    # except Exception as e:
    #     send_email_support('Payment capture failed', ['writartstudios@gmail.com', 'shwetabhartist@gmail.com'], f'{amount} - {current_user.name}\nRazorpay_payment_id: {response_data["razorpay_payment_id"]}','', '')

    # return render_template('order.html', logged_in=current_user.is_authenticated)


@payment.route('/ws_registration_success')
def ws_registration_success():
    return render_template('school/ws_registration_success.html', logged_in=current_user.is_authenticated)
