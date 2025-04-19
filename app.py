import os
from flask import Flask
from dotenv import load_dotenv
from extensions import mail, login_manager, db
from models.member import Member, member_role, member_workshop, Workshop, Role
from models.videos import Demo
from routes.account import account
from routes.main import main
from routes.manager import manager
from routes.payment import payment
from routes.school import school
from routes.gallery import gallery
from routes.studio import studio
from routes.animation_admin import animation_admin
from routes.client_section import client_section
from apscheduler.schedulers.background import BackgroundScheduler
from operations.artist_tools import delete_watermarked_images
from models.artist_data import ArtistData


load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('APP_SECRET')
# app.secret_key = 'giehgeriogn94tgih*H()g94t9hg'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///writart.db"
# app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_URI')
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
app.register_blueprint(gallery, url_prefix='/gallery')
app.register_blueprint(studio, url_prefix='/studio')
app.register_blueprint(client_section, url_prefix='/client_section')
app.register_blueprint(animation_admin, url_prefix='/animation_admin')

with app.app_context():
    db.create_all()


@login_manager.user_loader
def load_user(member_id):
    return db.get_or_404(Member, member_id)


# ------------------------------------------- SCHEDULED TASKS ---------------------------------------------- #


with app.app_context():
    scheduler = BackgroundScheduler(daemon=True)
    scheduler.add_job(delete_watermarked_images,
                      'interval',
                      minutes=1440)
    scheduler.start()


# ---------------------------------------------------------------------------------------------------------- #

if __name__ == '__main__':
    # app.run(host='0.0.0.0', port=5000)
    app.run(debug=True)
