from flask import Blueprint, render_template
import os


gallery = Blueprint('gallery', __name__, static_folder='static', template_folder='templates')


@gallery.route('/')
def home():
    folder_dir = "static/files/users/Shwetabh1/artworks"
    image_list = os.listdir(folder_dir)
    return render_template('gallery.html', img_list=image_list)