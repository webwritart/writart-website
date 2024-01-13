from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail, Message


db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()


image_dict = {
                'file': ['fb.png', 'insta.png', 'twitter.png'],
                'path': ['social-icons', 'social-icons', 'social-icons'],
                    }