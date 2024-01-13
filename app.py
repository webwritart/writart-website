import os
from flask import Flask
from extensions import db, mail, login_manager
from routes.account import account
from routes.main import main
from routes.school import school
from models.user import *
from routes.payment import payment
from routes.manager import manager


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get("APP_SECRET")
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///writart.db'
    app.config["MAIL_SERVER"] = 'smtp.gmail.com'
    app.config["MAIL_PORT"] = 465
    app.config["MAIL_USERNAME"] = os.environ.get('MAIL_USERNAME')
    app.config["MAIL_PASSWORD"] = os.environ.get('MAIL_PASSWORD')
    app.config["MAIL_USE_SSL"] = True
    mail.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)

    app.register_blueprint(main, url_prefix='/')
    app.register_blueprint(account, url_prefix='/account')
    app.register_blueprint(school, url_prefix='/school')
    app.register_blueprint(payment, url_prefix='/payment')
    app.register_blueprint(manager, url_prefix='/manager')

    @login_manager.user_loader
    def load_user(user_id):
        return db.get_or_404(User, user_id)


    return app
