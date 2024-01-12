from flask import Blueprint, render_template

account = Blueprint('account', __name__, static_folder='static', template_folder='templates')


@account.route('/')
def home():
    return render_template('my_account.html')