import os
from flask import Flask
from extensions import db
from routes.account import account
from routes.main import main
from routes.school import school


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get("APP_SECRET")
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///writart.db'

    db.init_app(app)

    app.register_blueprint(main, url_prefix='/')
    app.register_blueprint(account, url_prefix='/account')
    app.register_blueprint(school, url_prefix='/school')

    from models.payment import Payment
    from models.query import Query
    from models.role import Role
    from models.tool import Tools
    from models.user import user_workshop, user_role, User
    from models.workshop import Workshop
    from models.workshop_details import WorkshopDetails

    with app.app_context():
        db.create_all()

    return app
