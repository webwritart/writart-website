import time
from datetime import datetime
import pytz
from extensions import db, Message, mail
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from time import sleep
from urllib.parse import quote
import os
from flask import flash

load_dotenv()


def send_email_school(subject, recipients, body, html, image_dict):
    message = Message(subject, sender=("Writart Gurukul", 'writartstudios@gmail.com'), recipients=recipients)
    message.body = body
    if html:
        message.html = html
        root_path = 'static/images'
        if image_dict:
            for n in range(len(image_dict['file'])):
                file_format = 'image/' + image_dict['file'][n].split('.')[-1]
                message.attach(image_dict['file'][n], file_format,
                               open(os.path.join(root_path, image_dict['path'][n], image_dict['file'][n]), 'rb').read(),
                               'inline')
                # headers=[['content-ID', '<' + image_dict['file'][n].split('.')[0] + '>'], ])
    mail.send(message)


def send_email_studio(subject, recipients, body, html, image_dict):
    message = Message(subject, sender=("Writart Studio", 'writartstudios@gmail.com'), recipients=recipients)
    message.body = body
    if html:
        message.html = html
        root_path = '../static/images'
        if image_dict:
            for n in range(len(image_dict['file'])):
                file_format = 'image/' + image_dict['file'][n].split('.')[-1]
                message.attach(image_dict['file'][n], file_format,
                               open(os.path.join(root_path, image_dict['path'][n], image_dict['file'][n]), 'rb').read(),
                               'inline')
                # headers=[['content-ID', '<' + image_dict['file'][n].split('.')[0] + '>'], ])
    mail.send(message)


def send_email_support(subject, recipients, body, html, image_dict):
    message = Message(subject, sender=("Writart Support", "writartstudios@gmail.com"), recipients=recipients)
    message.body = body
    if html:
        message.html = html
        root_path = 'static/images'
        if image_dict:
            for n in range(len(image_dict['file'])):
                file_format = 'image/' + image_dict['file'][n].split('.')[-1]
                message.attach(image_dict['file'][n], file_format, open(os.path.join(root_path, image_dict['path'][n],
                                                                                     image_dict['file'][n]),
                                                                        'rb').read(), 'inline',)
                               # headers=[['content-ID', '<' + image_dict['file'][n].split('.')[0] + '>'], ])
    mail.send(message)
    print("Mail sent")


def send_wa_msg_by_list(wa_msg, num_list, name_list):
    options = webdriver.ChromeOptions()
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    options.add_argument("--profile-directory=Default")
    # options.add_argument("--user-data-dir=/var/tmp/chrome_user_data")
    # options.add_argument("--user-data-dir=/var/tmp/chrome_user_data")

    os.system("")
    os.environ["WDM_LOG_LEVEL"] = "0"

    class style():
        BLACK = '\033[30m'
        RED = '\033[31m'
        GREEN = '\033[32m'
        YELLOW = '\033[33m'
        BLUE = '\033[34m'
        MAGENTA = '\033[35m'
        CYAN = '\033[36m'
        WHITE = '\033[37m'
        UNDERLINE = '\033[4m'
        RESET = '\033[0m'

    print(style.BLUE)
    print("**********************************************************")
    print("**********************************************************")
    print("*****                                               ******")
    print("*****  THANK YOU FOR USING WHATSAPP BULK MESSENGER  ******")
    print("*****      This tool was built by Anirudh Bagri     ******")
    print("*****           www.github.com/anirudhbagri         ******")
    print("*****                                               ******")
    print("**********************************************************")
    print("**********************************************************")
    print(style.RESET)

    msg_path = "../routes/templates/wa_messages/"
    # msg_file = msg_path + msg_filename

    # f = open(msg_file, "r", encoding="utf8")
    # message = f.read()
    # f.close()
    msg = wa_msg
    print(style.YELLOW + '\nThis is your message-')
    print(style.GREEN + msg)
    print("\n" + style.RESET)
    numbers = num_list
    # numbers = []
    # f = open("numbers.txt", "r")
    # for line in f.read().splitlines():
    #     if line.strip() != "":
    #         numbers.append(line.strip())
    # f.close()
    total_number = len(numbers)
    print(style.RED + 'We found ' + str(total_number) + ' numbers in the file' + style.RESET)
    delay = 30

    # driver = webdriver.Chrome(executable_path='C:\drivers\chromedriver.exe', options=options)
    driver = webdriver.Chrome(options=options)
    print('Once your browser opens up sign in to web whatsapp')
    driver.get('https://web.whatsapp.com')
    # input(
    #     style.MAGENTA + "AFTER logging into Whatsapp Web is complete and your chats are visible, press ENTER..." + style.RESET)
    time.sleep(20)
    for idx, number in enumerate(numbers):
        number = number.strip()
        if number == "":
            continue
        print(style.YELLOW + '{}/{} => Sending message to {}.'.format((idx + 1), total_number, number) + style.RESET)
        try:
            message = msg.replace("[name]", name_list[idx])
            message = message.replace("|", "\n")
            print(message)
            message = quote(message)
            url = 'https://web.whatsapp.com/send?phone=' + number + '&text=' + message
            sent = False
            for i in range(3):
                if not sent:
                    driver.get(url)
                    try:
                        click_btn = WebDriverWait(driver, delay).until(
                            EC.element_to_be_clickable(
                                (By.XPATH, '//*[@id="main"]/footer/div[1]/div/span/div/div[2]/div[2]/button/spa')))
                        message = msg
                    except Exception as e:
                        print(style.RED + f"\nFailed to send message to: {number}, retry ({i + 1}/3)")
                        print("Make sure your phone and computer is connected to the internet.")
                        print("If there is an alert, please dismiss it." + style.RESET)
                        if i == 2:
                            indiatz = pytz.timezone("Asia/Kolkata")
                            now = datetime.now(indiatz)
                            with open('wa_log.txt', 'a') as the_file:
                                the_file.write(f' --- Failed to send message to\n')
                            print("The problem logged")
                    else:
                        sleep(1)
                        click_btn.click()
                        sent = True
                        sleep(3)
                        print(style.GREEN + 'Message sent to: ' + number + style.RESET)
        except Exception as e:
            print(style.RED + 'Failed to send message to ' + number + str(e) + style.RESET)

    driver.close()


def send_email_school_and_wa_msg_by_list(subject, recipients, body, html, image_dict, wa_msg, num_list, name_list):
    send_email_school(subject, recipients, body, html, image_dict)
    send_wa_msg_by_list(wa_msg, num_list, name_list)

