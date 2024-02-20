from PIL import Image, ImageDraw, ImageFont
import os
import datetime
from operations.miscellaneous import log
from extensions import db
from flask_login import current_user


def add_watermark(input_path, watermark_text, output_path, color):
    global col_code
    if color == 'black':
        col_code = (0, 0, 0, 50)
    elif color == 'white':
        col_code = (255, 255, 255, 50)
    input_image = Image.open(input_path)
    input_image = input_image.convert('RGBA')
    txt = Image.new("RGBA", input_image.size, (255, 255, 255, 0))

    width, height = input_image.size
    draw = ImageDraw.Draw(txt)
    text = watermark_text

    font_size = int(width/50)
    font = ImageFont.truetype('/home/writart/website/static/fonts/Arial.ttf', font_size)
    # font = ImageFont.truetype('arial.ttf', font_size)
    ascent, descent = font.getmetrics()

    text_width = font.getmask(watermark_text).getbbox()[2]

    n = 1
    n2 = 1
    for i in range(3):
        y = (n2/4)*height
        for j in range(3):
            x = (n/4)*width - 0.5*text_width
            draw.text((x, y), text, font=font, fill=col_code)
            n += 1
        n2 += 1
        n = 1

    out = Image.alpha_composite(input_image, txt)
    out = out.convert("RGB")
    out.save(output_path)
    os.remove(input_path)
    file_final_size = os.path.getsize(output_path)
    return file_final_size


def delete_watermarked_images():
    all_users = os.listdir("static/files/users")
    memory_occupied_total = current_user.artist_data.memory_occupied_total
    file_size = 0
    for user in all_users:
        path = f"static/files/users/{user}/watermark_output"
        all_files = os.listdir(path)
        try:
            for file in all_files:
                file_path = f"{path}/{file}"
                creation_date = datetime.datetime.fromtimestamp(os.path.getctime(file_path))
                today = datetime.datetime.today()
                delta = today - creation_date
                if delta.days > 7:
                    file_size += os.path.getsize(file_path)
                    os.remove(file_path)
                    log("Watermarked images older than 7 days deleted successfully!", "success")
            current_user.artist_data.memory_occupied_total = memory_occupied_total - file_size
            db.session.commit()

        except Exception as e:
            print(e)


def delete_single_watermarked_image(path):
    file_size = os.path.getsize(path)
    memory_occupied_total = current_user.artist_data.memory_occupied_total
    os.remove(path)
    current_user.artist_data.memory_occupied_total = memory_occupied_total - file_size
    db.session.commit()


def delete_all_from_user(folder):
    path = f"static/files/users/{folder}/watermark_output"
    file_size = 0
    memory_occupied_total = current_user.artist_data.memory_occupied_total

    file_list = os.listdir(path)
    for file in file_list:
        file_path = f"{path}/{file}"
        file_size += os.path.getsize(file_path)
        os.remove(file_path)

    current_user.artist_data.memory_occupied_total = memory_occupied_total - file_size
    db.session.commit()

