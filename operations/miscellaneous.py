import datetime
import os
import PIL.Image as Image
from flask_sqlalchemy import table
from extensions import db


def calculate_age(birthdate):
    year, month, day = map(int, birthdate.split("-"))
    today = datetime.date.today()
    age = today.year - year - ((today.month, today.day) < (month, day))
    return age


def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


def log(text, category):
    today = str(datetime.date.today())
    if category == 'error':
        text = f"        <p style='line-height:0.1;'> {today} - <span style='color:red;'>{text}</span> </p>\n"
    elif category == 'success':
        text = f"        <p style='line-height:0.1;'> {today} - <span style='color:green;'>{text}</span> </p>\n"
    elif category == 'routine':
        text = f"        <p style='line-height:0.1;'> {today} - <span style='color:yellow;'>{text}</span> </p>\n"
    elif category == 'none':
        text = f"        <p style='line-height:0.1;'> {today} - <span style='color:white;'>{text}</span> </p>\n"
    with open("./routes/templates/manager/log.html", "r") as f:
        contents = f.readlines()
        lines = len(contents)
        index = lines - 4
        contents.insert(index, text)
    with open("./routes/templates/manager/log.html", "w") as f:
        contents = "".join(contents)
        f.write(contents)
        f.close()
    print("logged into log.txt successfully")


import_folder = '../static/files/users/Shwetabh1/artworks/'
output_thumbnail_folder = '../static/files/users/Shwetabh1/artworks/thumbnail/'
output_large_folder = '../static/files/users/Shwetabh1/artworks/large/'


def image_resize_and_compress_bulk(input_folder, output_folder, image_type, quality):
    for f in os.listdir(input_folder):
        new_height = ''
        if os.path.isfile(input_folder+f):
            image = Image.open(input_folder+f)
            width, height = image.size

            w_h_ratio = round(width / height, 3)
            if image_type == 't':
                new_height = 500
            elif image_type == 'l':
                new_height = 1000
            else:
                print('Wrong image type!')
            new_width = round(new_height * w_h_ratio)

            image.thumbnail((new_width, new_height), Image.Resampling.LANCZOS)
            image.save(output_folder+f, optimize=True, quality=quality)
            print('Resize successful!')



