import datetime
import os
import PIL.Image as Image
from difflib import SequenceMatcher
from flask_sqlalchemy import table
from extensions import db, p
from captcha.image import ImageCaptcha
import random
import base64
from PIL import Image, ImageDraw, ImageFont



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


def image_resize_and_compress_single(filename, root_path,):
    new_l_width = 0
    new_l_height = 0
    if root_path[-1] != '/':
        root_path = root_path + '/'
    thumbnail_folder = root_path + 'thumbnail/'
    large_folder = root_path + 'large/'
    os.makedirs(thumbnail_folder, exist_ok=True)
    os.makedirs(large_folder, exist_ok=True)
    thumbnail_filename = filename.split('.')[0] + '_thumbnail.' + filename.split('.')[1]
    large_filename = filename.split('.')[0] + '_large.' + filename.split('.')[1]
    width = 0
    height = 0

    image_path = root_path + filename
    with Image.open(image_path) as image:
        width, height = image.size
        aspect_ratio = width/height

        # -------------------------------------- THUMBNAIL -------------------------------------- #
        if width > height:
            new_t_width = 400
            new_t_height = round(400/aspect_ratio)
        else:
            new_t_height = 400
            new_t_width = round(400*aspect_ratio)
        image.thumbnail((new_t_width, new_t_height), Image.Resampling.LANCZOS)
        if filename.split('.')[1] is 'PNG' or 'png':
            image.convert('RGB')
            thumbnail_filename = thumbnail_filename.split('.')[0] + '.jpg'
        image.save(thumbnail_folder+thumbnail_filename, optimize=True, quality=100)

    # ---------------------------------------- LARGE ---------------------------------------- #
    with Image.open(image_path) as image_2:
        if height > 2100:
            new_l_height = 2100
            new_l_width = round(2100*aspect_ratio)
            image_2.thumbnail((new_l_width, new_l_height), Image.Resampling.LANCZOS)
            if filename.split('.')[1] is 'PNG' or 'png':
                image.convert('RGB')
                large_filename = large_filename.split('.')[0] + '.jpg'
            image_2.save(large_folder + large_filename, optimize=True, quality=75)
        else:
            if filename.split('.')[1] is 'PNG' or 'png':
                image.convert('RGB')
                large_filename = large_filename.split('.')[0] + '.jpg'
            image_2.save(large_folder + large_filename, optimize=True, quality=75)


    os.remove(image_path)
    print('Image Resize Successful')


def text_match(target, options_list):
    def similarity_ratio(a, b):
        return SequenceMatcher(None, a, b).ratio()

    best_match = max(options_list, key=lambda option: similarity_ratio(target, option))
    match_ratio = f'{int(similarity_ratio(target, best_match)*100)}%'
    return best_match, match_ratio


def generate_captcha():
    captcha_num = str(random.randrange(100000, 999999))
    img = ImageCaptcha()
    captcha_io = img.generate(captcha_num)
    binary_data = captcha_io.getvalue()
    encoded_data_bytes = base64.b64encode(binary_data)
    encoded_string = encoded_data_bytes.decode('utf-8')
    captcha_uri = f"data:image/png;base64, {encoded_string}"
    return captcha_num, captcha_uri


def prepare_certificate(awardee_name_text, course_topic, course_period, issuing_date, certificate_id, ws_uuid, user_uuid, user_name, export_path):
    image = Image.open("./static/images/miscellaneous/Participation-Certificate.jpg")
    draw = ImageDraw.Draw(image)

    name_word_list = awardee_name_text.split(' ')
    name_word_count = len(name_word_list)
    if name_word_count > 2:
        del name_word_list[2:]
        awardee_name = " ".join(name_word_list)
    else:
        awardee_name = awardee_name_text
    course_topic = f"{course_topic} (Course)"
    course_period = f"({course_period})"
    certificate_id = str(certificate_id)

    primary_text_color = (100, 117, 0)
    secondary_text_color = (0, 0, 0)
    awardee_name_font_size = 80
    course_topic_font_size = 40
    course_period_font_size = 36
    issuing_date_font_size = 30
    certificate_id_font_size = 30
    
    center_x = image.width // 2

    name_y = 610
    topic_y = 775
    period_y = 830
    issuing_y = 1090
    id_y = 1138


    name_font = ImageFont.truetype("arial.ttf", size=awardee_name_font_size)
    topic_font = ImageFont.truetype("arial.ttf", size=course_topic_font_size)
    period_font = ImageFont.truetype("arial.ttf", size=course_period_font_size)
    issuing_font = ImageFont.truetype("arial.ttf", size=issuing_date_font_size)
    certificate_id_font = ImageFont.truetype("arial.ttf", size=certificate_id_font_size)

    draw.text((center_x, name_y), awardee_name, fill=primary_text_color, font=name_font, anchor='mm')
    draw.text((center_x, topic_y), course_topic, fill=primary_text_color, font=topic_font, anchor='mm')
    draw.text((center_x, period_y), course_period, fill=primary_text_color, font=period_font, anchor='mm')
    draw.text((1470, issuing_y), issuing_date, fill=secondary_text_color, font=issuing_font)
    draw.text((1470, id_y), certificate_id, fill=secondary_text_color, font=certificate_id_font)


    if image.mode != 'RGB':
        image = image.convert('RGB')


    if not os.path.exists(export_path):
            os.makedirs(export_path)
    file_name = f"certificate_{ws_uuid}_{user_uuid}_{user_name}.pdf"
    file_path = export_path + file_name
    
    image.save(file_path, 'PDF', resolution=100.0)