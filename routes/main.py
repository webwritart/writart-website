from flask import Blueprint, render_template

main = Blueprint('main', __name__, static_folder='static', template_folder='templates')


@main.route('/')
def home():
    return render_template('index.html')