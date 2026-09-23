from functools import wraps
from flask import abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from flask_mail import Mail, Message
from datetime import datetime
from pathlib import Path

from sqlalchemy.sql.coercions import RoleImpl

db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()


image_dict = {
                'file': ['fb.png', 'insta.png', 'twitter.png'],
                'path': ['social-icons', 'social-icons', 'social-icons'],
                    }

current_year = datetime.now().year


# def admin_only(f):
#     @wraps(f)
#     def decorated_function(*args, **kwargs):
#         admin = db.session.query(Role)
#         if current_user.role.name != 'admin':
#             return abort(403)
#         return f(*args, **kwargs)
#
#     return decorated_function

def p(text):
    print(f"\033[37m{text}\033[0m")