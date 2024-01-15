import os
from flask import Blueprint, render_template, request, flash, send_file, redirect, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from extensions import db, image_dict
from messenger import send_email_school, send_email_support
from models.user import User, Workshop
from flask_login import current_user, login_required, login_user, logout_user
from datetime import date
import random


account = Blueprint('account', __name__, static_folder='static', template_folder='templates')

otp = random.randint(1000, 9999)
today_date = date.today()


@login_required
@account.route('/', methods=['GET', 'POST'])
def home():
    if len(current_user.participated) > 0:
        certificate = True
    else:
        certificate = False

    if request.method == 'POST':
        if request.form.get('whatsapp'):
            current_user.whatsapp = request.form.get("whatsapp")
        if request.form.get('profession'):
            current_user.profession = request.form.get("profession")
        if request.form.get('name'):
            current_user.name = request.form.get("name")
        if request.form.get('state'):
            current_user.state = request.form.get('state')
        if request.form.get('phone'):
            phone = request.form.get('phone')
            result = db.session.execute(db.select(User).where(User.phone == phone))
            user = result.scalar()
            if user:
                flash("Couldn't update number as there's already an account with this number", category="error")
            else:
                current_user.phone = request.form.get("phone")
        if request.form.get('email'):
            mail_ = request.form.get('email')
            result2 = db.session.execute(db.select(User).where(User.email == mail_))
            user2 = result2.scalar()
            if user2:
                flash("Couldn't update email as there's already an account with this email", category="error")
            else:
                current_user.email = request.form.get("email")

        if request.form.get('old-pwd'):
            old_pwd = request.form.get('old-pwd')
            if not check_password_hash(current_user.password, old_pwd):
                flash("Please enter the correct old password", category="error")
            else:
                hash_and_salted_password = generate_password_hash(
                    request.form.get('new-pwd'),
                    method='pbkdf2:sha256',
                    salt_length=8
                )
                current_user.password = hash_and_salted_password
                flash("Password changed successfully", category="success")
        if request.form.get('fb-url'):
            if 'https://' not in request.form.get('fb-url'):
                fb_url = 'https://' + request.form.get('fb-url')
            else:
                fb_url = request.form.get('fb-url')
            current_user.fb_url = fb_url
        if request.form.get('insta-url'):
            if 'https://' not in request.form.get('insta-url'):
                insta_url = 'https://' + request.form.get('insta-url')
            else:
                insta_url = request.form.get('fb-url')
            current_user.insta_url = insta_url
        if request.form.get('web-url'):
            if 'https://' not in request.form.get('web-url'):
                website = 'https://' + request.form.get('web-url')
            else:
                website = request.form.get('web-url')
            current_user.website = website

        db.session.commit()

        if request.form.get('submit') == 'download-certificate':
            print('button working!')
            folder_name = current_user.name.split()[0] + str(current_user.id)
            last_workshop_name = current_user.participated[len(current_user.participated) - 1].name
            second_last_workshop_name = current_user.participated[len(current_user.participated) - 2].name
            topic = current_user.participated[len(current_user.participated) - 1].topic
            topic2 = current_user.participated[len(current_user.participated) - 2].topic
            file_name = f"{last_workshop_name}-{current_user.name.split()[0]}.pdf"
            file_name_2 = f"{second_last_workshop_name}-{current_user.name.split()[0]}.pdf"
            print('variables set successfully')
            path = f"../static/files/users/{folder_name}/certificates/{file_name}"
            path2 = f"../static/files/users/{folder_name}/certificates/{file_name_2}"
            print('path is okay!')
            if os.path.exists(path):
                return send_file(path_or_file=path, as_attachment=True,
                                 download_name=f"Certificate - {topic} - Writart Gurukul.pdf")
            elif os.path.exists(path2):
                return send_file(path_or_file=path2, as_attachment=True,
                                 download_name=f"Certificate - {topic2} - Writart Gurukul.pdf")
            else:
                flash('The Certificate is to be uploaded soon!', 'error')
            print('path checked successfully')

        topic_list = []
        result = current_user.participated
        for r in result:
            topic_list.append(r.topic)
        if request.form.get('submit') in topic_list:
            index = topic_list.index(request.form.get('submit'))
            ws = db.session.query(Workshop).filter_by(topic=topic_list[index]).one()
            folder_name = current_user.name.split()[0] + str(current_user.id)
            file_name = f"{ws.name}-{current_user.name.split()[0]}.pdf"
            path = f"../static/files/users/{folder_name}/certificates/{file_name}"
            return send_file(path_or_file=path, as_attachment=True,
                             download_name=f"Certificate - {topic_list[index]} - Writart Gurukul.pdf")

        return redirect(url_for('account.home'))

    certificate_list = []
    if len(current_user.participated) > 0:
        for workshop in current_user.participated:
            file_name = f"{workshop.name}-{current_user.name.split()[0]}.pdf"
            folder_name = current_user.name.split()[0] + str(current_user.id)
            path = f"../static/files/users/{folder_name}/certificates/{file_name}"
            if os.path.exists(path):
                certificate_list.append(workshop.topic)
    return render_template('my_account.html', certificate_list=certificate_list, certificate=certificate,
                           name=current_user.name, logged_in=current_user.is_authenticated)


@account.route('/register', methods=['GET', 'POST'])
def register():
    num_list = []
    result = db.session.query(User)
    for user in result:
        num = user.phone
        if len(num) == 10:
            user_no = f"91{num}"
        elif len(num) == 11 and num[0] == '0':
            user_no = f'91{num[1:]}'
        elif len(num) == 12 and num[:2] == '91':
            user_no = num
        elif len(num) == 13:
            user_no = num[3:]
        else:
            user_no = num
        num_list.append(user_no)

    if request.method == 'POST':
        ph = request.form.get('phone')
        if len(ph) == 10:
            phone = f"91{ph}"
        elif len(ph) == 11 and ph[0] == '0':
            phone = f'91{ph[1:]}'
        elif len(ph) == 12 and ph[:2] == '91':
            phone = ph
        elif len(ph) == 13:
            phone = ph[3:]
        else:
            phone = ph

        email = request.form.get('email')
        state = request.form.get('state')
        result = db.session.execute(db.select(User).where(User.email == email))
        user = result.scalar()
        if user:
            flash("You've already signed up with that email, log in instead!", "error")
            return redirect(url_for('account.login'))
        if phone in num_list:
            flash("Already an account exists with phone number. Please register with different phone number or log in",
                  "error")
            return redirect(url_for('account.register'))
        hash_and_salted_password = generate_password_hash(
            request.form.get('password'),
            method='pbkdf2:sha256',
            salt_length=8
        )
        date_ = request.form.get('date')
        if len(date_) < 2:
            date_ = "0" + date_
        month = request.form.get('month')
        if len(month) < 2:
            month = "0" + month
        year = request.form.get('year')
        dob = f"{year}-{month}-{date_}"

        new_user = User(
            email=request.form.get('email'),
            password=hash_and_salted_password,
            name=request.form.get('name'),
            phone=request.form.get('phone'),
            whatsapp=request.form.get('whatsapp'),
            profession=request.form.get('profession'),
            sex=request.form.get('sex'),
            dob=dob,
            state=state,
            registration_date=today_date
        )

        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        mail = render_template('mails/registration_success.html')
        send_email_school('Registration success!', [email],
                          '',
                          mail, image_dict)
        return redirect(url_for('account.home', name=current_user.name.split()[0]))
    return render_template("register.html", logged_in=current_user.is_authenticated)


@account.route('/login', methods=['GET', 'POST'])
def login():
    num_list = []
    raw_num_list = []
    result = db.session.query(User)
    for user in result:
        print(user)
        num = user.phone
        raw_num_list.append(num)
        if len(num) == 10:
            user_no = f"91{num}"
        elif len(num) == 11 and num[0] == '0' or '+':
            user_no = f'91{num[1:]}'
        elif len(num) == 12 and num[:2] == '91':
            user_no = num
        elif len(num) == 13 and num[:3] == '+91':
            user_no = num[3:]
        else:
            user_no = num
        num_list.append(user_no)
    if request.method == 'POST':
        data = request.form.get('email-phone')
        if '@' in data:
            email = data
            result = db.session.execute(db.select(User).where(User.email == email))
            user = result.scalar()
        else:
            user_phone = ''
            ph = data
            if len(ph) == 10:
                phone = f"91{ph}"
            elif len(ph) == 11 and ph[0] == '0' or '+':
                phone = f'91{ph[1:]}'
            elif len(ph) == 12 and ph[:2] == '91':
                phone = ph
            elif len(ph) == 13 and ph[:3] == '+91':
                phone = ph[3:]
            else:
                phone = ph
            if phone in num_list:
                index = num_list.index(phone)
                user_phone = raw_num_list[index]
            result = db.session.execute(db.select(User).where(User.phone == user_phone))
            user = result.scalar()
        password = request.form.get('password')

        # Email or Phone doesn't exist or password incorrect:
        if not user:
            flash("That Email or Phone does not exist, please try again.", category="error")
        elif not check_password_hash(user.password, password):
            flash('Password incorrect, please try again.', category='error')
        else:
            login_user(user)
            return redirect(url_for('account.home', name=current_user.name.split()[0]))

    return render_template("login.html")


email_list = []


@account.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        if request.form.get('email'):
            email = request.form.get('email')
            email_list.append(email)
            user_mail_list = []
            results = db.session.query(User)
            for result in results:
                user_mail_list.append(result.email)
            if email in user_mail_list:
                send_email_support(subject="Password reset",
                                   recipients=email_list, body='',
                                   html=render_template('mails/password_reset_link.html',
                                                        link=f"http://127.0.0.1:5000/account/set_new_password?otp={otp}"),
                                   image_dict=image_dict)
                return render_template('check_mail_notification.html')
            else:
                flash('No account found with the entered email!', 'error')

        if request.form.get('password'):
            new_pwd = request.form.get('password')
            hash_and_salted_password = generate_password_hash(
                new_pwd,
                method='pbkdf2:sha256',
                salt_length=8
            )
            result = db.session.execute(db.select(User).where(User.email == email_list[0]))
            user = result.scalar()
            user.password = hash_and_salted_password

            db.session.commit()
            login_user(user)
            flash('New password set successfully!', 'success')
            mail = render_template('mails/password_reset_notification.html')
            send_email_support('Password Reset', [current_user.email],
                               '',
                               mail, image_dict)
            return redirect(url_for('account.home'))

    return render_template("forgot_password.html")


@account.route('/set_new_password', methods=['GET', 'POST'])
def set_new_password():
    entered_otp = request.args.get('otp')
    if str(otp) == str(entered_otp):
        return render_template('set_new_password.html')
    else:
        send_email_support('ERROR!!!', ['shwetabh@writart.com'], 'Problem forget password reset', '', '')
        return redirect(url_for("account.login"))


@account.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.home'))
