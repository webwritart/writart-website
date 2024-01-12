import os

from flask import Flask
from .extensions import db
from .routes import main, account, school


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get("APP_SECRET")
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///writart.db'

    db.init_app(app)

    app.register_blueprint(main.main, url_prefix='/')
    app.register_blueprint(account.account, url_prefix='/account')
    app.register_blueprint(school.school, url_prefix='/school')

    return app
