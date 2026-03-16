from functools import wraps
from flask import abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from flask_mail import Mail, Message
from datetime import datetime
from pathlib import Path


db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()


image_dict = {
                'file': ['fb.png', 'insta.png', 'twitter.png'],
                'path': ['social-icons', 'social-icons', 'social-icons'],
                    }

current_year = datetime.now().year


def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.role.name != 'admin':
            return abort(403)
        return f(*args, **kwargs)

    return decorated_function

def list_files_in_directory(directory_path):
    p = Path(directory_path)
    # Use a list comprehension to filter for files only
    files = [item for item in p.iterdir() if item.is_file()]
    return files

def list_folders_in_directory(path_string):
    p = Path(path_string)
    # Filter for entries that are directories and return their Path objects
    folders = [item for item in p.iterdir() if item.is_dir()]
    return folders