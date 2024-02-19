from PIL import Image, ImageDraw, ImageFont
import os
import datetime
from operations.miscellaneous import log


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


def delete_watermarked_images():
    all_users = os.listdir("static/files/users")
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
                    os.remove(file_path)
                    log("Watermarked images older than 7 days deleted successfully!", "success")

        except Exception as e:
            print(e)


def delete_single_watermarked_image(path):
    os.remove(path)