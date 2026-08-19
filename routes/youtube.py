from flask import Blueprint, render_template, request, redirect, flash, send_file, session, url_for, jsonify
from flask_login import current_user
from extensions import db, current_year,p


youtube = Blueprint('youtube', __name__, static_folder='static', template_folder='templates/youtube')


@youtube.route('/', methods=['GET', 'POST'])
def home():
    return render_template('youtube.html', logged_in=current_user.is_authenticated)
