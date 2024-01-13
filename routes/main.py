from flask import Blueprint, render_template
from extensions import login_manager, db
from models.user import User
from flask_login import current_user

main = Blueprint('main', __name__, static_folder='static', template_folder='templates')


@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)


@main.route('/')
def home():
    return render_template('index.html', logged_in=current_user.is_authenticated)
