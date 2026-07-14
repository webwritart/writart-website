from datetime import datetime, date
import os
import PIL.Image as Image
from difflib import SequenceMatcher
from flask_sqlalchemy import table
from extensions import db, p
from captcha.image import ImageCaptcha
import random
import base64
from PIL import Image, ImageDraw, ImageFont
import shutil
from models.tool import Tools
from pathlib import Path



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
        if filename.split('.')[1] == 'PNG' or 'png':
            image.convert('RGB')
            thumbnail_filename = thumbnail_filename.split('.')[0] + '.jpg'
        image.save(thumbnail_folder+thumbnail_filename, optimize=True, quality=100)

    # ---------------------------------------- LARGE ---------------------------------------- #
    with Image.open(image_path) as image_2:
        if height > 2100:
            new_l_height = 2100
            new_l_width = round(2100*aspect_ratio)
            image_2.thumbnail((new_l_width, new_l_height), Image.Resampling.LANCZOS)
            if filename.split('.')[1] == 'PNG' or 'png':
                image.convert('RGB')
                large_filename = large_filename.split('.')[0] + '.jpg'
            image_2.save(large_folder + large_filename, optimize=True, quality=75)
        else:
            if filename.split('.')[1] == 'PNG' or 'png':
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


def prepare_invoice(customer_name, customer_address, customer_phone, customer_email, item_dict, tax_percent, date_, user_uuid):
    image = Image.open("./static/images/miscellaneous/invoice_base_design.png")
    if image.mode != 'RGBA':
        image = image.convert('RGBA')
    draw = ImageDraw.Draw(image)

    date_today = str(date_)
    if not date_:
        date_today = str(date.today())
    
    large_name = True
    while large_name:
        if len(customer_name) > 26:
            customer_name = customer_name.split(' ')
            customer_name.pop()
            customer_name = " ".join(customer_name)
        else:
            large_name = False
    
    
    # ---------------------------------- INVOICE NO -------------------------------------- #
    last_invoice_no = db.session.query(Tools).filter_by(keyword='last_invoice').scalar().data
    current_invoice_no = f"INV-8000{int(last_invoice_no)+1}"
    db.session.query(Tools).filter_by(keyword='last_invoice').scalar().data = int(last_invoice_no)+1
    db.session.commit()
    
    primary_text_color = (0, 0, 0)
    secondary_text_color = (0, 0, 0, 200)
    tertiary_text_color = (255,255,255)
    primary_font_size = 47
    secondary_font_size = 35
    tertiary_font_size = 35
    numeral_primary_size = 33
    numeral_bold_size = 40
    
    # ----------------------- Position coordinates --------------------------------------- #
    customer_name_coord = (129, 625)
    customer_address_coord = (129, 675)
    customer_phone_coord = (250, 727)
    invoice_no_coord = (1020, 680)
    date_coord = (1020, 730)

    # ---------------------------- Font -------------------------------------------------- #
    primary_font = ImageFont.truetype("./static/fonts/myriad_pro/MYRIADPRO-BOLD.OTF", size=primary_font_size)
    secondary_font = ImageFont.truetype("./static/fonts/arial/ARIALBD.TTF", size=secondary_font_size)
    tertiary_font = ImageFont.truetype("./static/fonts/myriad_pro/MyriadPro-Light.otf", size=tertiary_font_size)
    numeral_primary_font = ImageFont.truetype("./static/fonts/myriad_pro/MyriadPro-Light.otf", size=numeral_primary_size)
    numeral_bold_font = ImageFont.truetype("./static/fonts/arial/ARIBLK.TTF", size=numeral_bold_size)

    draw.text(customer_name_coord, customer_name, fill=primary_text_color, font=primary_font)
    draw.text(customer_address_coord, customer_address, fill=primary_text_color, font=tertiary_font)
    draw.text(customer_phone_coord, customer_phone, fill=primary_text_color, font=numeral_primary_font)
    draw.text(invoice_no_coord, current_invoice_no, fill=primary_text_color, font=numeral_primary_font)
    draw.text(date_coord, date_today, fill=primary_text_color, font=numeral_primary_font)
    draw.text(date_coord, date_today, fill=primary_text_color, font=numeral_primary_font)
    
    grand_total = 0
    y = 935
    y2 = 930
    for item in item_dict:
        item_serial = item + '.'
        item_description = item_dict[item]['item_description']
        price = item_dict[item]['price']
        price_entry = f"₹{item_dict[item]['price']}"
        qty = item_dict[item]['qty']
        total = int(price) * int(qty)
        total_entry = f"₹{int(price) * int(qty):,}"
        item_serial_coord = (129, y2)
        item_description_coord = (180, y2)
        price_coord = (1035, y)
        qty_coord = (1280, y)
        total_coord = (1552, y)
        draw.text(item_serial_coord, item_serial, fill=secondary_text_color, font=secondary_font)
        draw.text(item_description_coord, item_description, fill=(secondary_text_color), font=secondary_font)
        draw.text(price_coord, price_entry, fill=secondary_text_color, font=secondary_font, anchor='ra')
        draw.text(qty_coord, qty, fill=secondary_text_color, font=secondary_font, anchor='ra')
        draw.text(total_coord, total_entry, fill=secondary_text_color, font=secondary_font, anchor='ra')
        y+=70
        y2+=70
        grand_total += total
    
    if tax_percent:
        tax_amount = round((int(tax_percent)/100)*grand_total)
        tax_amount_entry = f"₹{tax_amount:,}"
        grand_total_entry = f"₹{round(grand_total + (int(tax_percent)/100)*grand_total):,}"

        tax = f"Tax GST {tax_percent}%"
        tax_coord = (1070, 1640)
        tax_amount_coord = (1560, 1660)
        draw.text(tax_coord, tax, fill=secondary_text_color, font=secondary_font)
        draw.text(tax_amount_coord, tax_amount_entry, fill=secondary_text_color, font=secondary_font, anchor='rm')
    else:
        grand_total_entry = f"₹{round(grand_total):,}"
    
    grand_total_coord = (1565, 1735)
    draw.text(grand_total_coord, grand_total_entry, fill=primary_text_color, font=numeral_bold_font, anchor='rm')
    save_path = f"./static/files/users/{user_uuid}/documents/invoices/"
    
    if save_path[-1] != '/':
        save_path + '/'
    temp_img_path = f'{save_path}temp_img/'
    if not os.path.exists(temp_img_path):
        os.makedirs(temp_img_path)
    filename = f"{user_uuid}_{current_invoice_no}"
    temp_img_filepath = temp_img_path+filename+'.png'

    image.save(temp_img_filepath, 'PNG', resolution=100.0)


def png_to_pdf(file_directory, export_path):
    dir_path = Path(file_directory)
    files = [str(f) for f in dir_path.iterdir() if f.is_file()]
    if export_path[-1] != '/':
        export_path = export_path + '/'
    for file in files:
        img = Image.open(file)
        rgb_img = img.convert('RGB')
        filename = Path(file).stem
        rgb_img.save(export_path + filename + '.pdf')
    p('Converted png to pdf')




def move_files (source_path_with_file_joined_list, destination_folder):
    if not os.path.exists(destination_folder):
            os.makedirs(destination_folder)
    for file_path in source_path_with_file_joined_list:
        if os.path.exists(file_path):
            dir, file_name = os.path.split(file_path)
            dest_path = os.path.join(destination_folder, file_name)
            shutil.move(file_path, dest_path)
            p("File moved successfully!")
        else:
            p("File doesn't exit")


def create_uuid(existing_uuid_list, uuid_length_in_digit):
    lower_limit = '1'
    upper_limit = '9'
    uuid = ''
    for i in range(uuid_length_in_digit-1):
        lower_limit = lower_limit + '0'
    
    for i in range(uuid_length_in_digit-1):
        upper_limit = upper_limit + '9'
    
    carry_on = True
    while carry_on:
        uuid = random.randint(int(lower_limit), int(upper_limit))
        if uuid not in existing_uuid_list:
            carry_on = False
            
    return uuid


