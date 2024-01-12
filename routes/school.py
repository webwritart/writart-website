from flask import Blueprint, render_template


school = Blueprint('school', __name__, static_folder='static', template_folder='templates')


@school.route('/')
def home():
    render_template('courses.html')