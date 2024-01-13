import os
from flask import Flask
from extensions import db, mail
from routes.account import account
from routes.main import main
from routes.school import school


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

    app.register_blueprint(main, url_prefix='/')
    app.register_blueprint(account, url_prefix='/account')
    app.register_blueprint(school, url_prefix='/school')

    return app
