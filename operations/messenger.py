import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from extensions import db, Message, mail
from dotenv import load_dotenv

load_dotenv()


def send_email_school(subject, recipients, body, html, image_dict):
    message = Message(subject, sender=("Writart Gurukul", "admin@writart.com"), recipients=recipients)
    message.body = body
    if html:
        message.html = html
        root_path = 'static/images'
        if image_dict:
            for n in range(len(image_dict['file'])):
                file_format = 'image/' + image_dict['file'][n].split('.')[-1]
                message.attach(image_dict['file'][n], file_format,
                               open(os.path.join(root_path, image_dict['path'][n], image_dict['file'][n]), 'rb').read(),
                               'inline', headers=[['content-ID', '<' + image_dict['file'][n].split('.')[0] + '>'], ])
    mail.send(message)


def send_email_studio(subject, recipients, body, html, image_dict):
    message = Message(subject, sender=("Writart Studio", "shwetabh@writart.com"), recipients=recipients)
    message.body = body
    if html:
        message.html = html
        root_path = '../static/images'
        if image_dict:
            for n in range(len(image_dict['file'])):
                file_format = 'image/' + image_dict['file'][n].split('.')[-1]
                message.attach(image_dict['file'][n], file_format,
                               open(os.path.join(root_path, image_dict['path'][n], image_dict['file'][n]), 'rb').read(),
                               'inline', headers=[['content-ID', '<' + image_dict['file'][n].split('.')[0] + '>'], ])
    mail.send(message)


def send_email_support(subject, recipients, body, html, image_dict):
    message = Message(subject, sender=("Writart Support", "shwetabh@writart.com"), recipients=recipients)
    message.body = body
    if html:
        message.html = html
        root_path = '../static/images'
        if image_dict:
            for n in range(len(image_dict['file'])):
                file_format = 'image/' + image_dict['file'][n].split('.')[-1]
                message.attach(image_dict['file'][n], file_format, open(os.path.join(root_path, image_dict['path'][n],
                                                                                     image_dict['file'][n]),
                                                                        'rb').read(), 'inline',
                               headers=[['content-ID', '<' + image_dict['file'][n].split('.')[0] + '>'], ])
    mail.send(message)


def send_wa_message_by_db(wa_message, db_table_name):
    wa_num_list = []
    name_list = []
    mail_list = []

    wa_num_list.insert(0, '918920351265')
    wa_num_list.insert(1, '918920351265')
    name_list.insert(0, 'Test')
    name_list.insert(1, 'Test2')
    mail_list.insert(0, 'test@mail.com')
    mail_list.insert(1, 'test2@gmail.com')
    users = db.session.query(db_table_name)
    success_count = 0
    # ----------------------------------- Filtering Duplicates out ------------------------------------------ #

    for user in users:
        if user.email not in mail_list:
            mail_list.append(user.email)
            if user.whatsapp:
                if len(user.whatsapp) == 10:
                    wa_num_list.append(f'91{user.whatsapp}')
                elif len(user.whatsapp) == 11 and user.whatsapp[0] == '0':
                    wa_num_list.append(f'91{user.whatsapp[1:]}')
                elif len(user.whatsapp) == 12 and user.whatsapp[:2] == '91':
                    wa_num_list.append(user.whatsapp)
                elif user.whatsapp[:1] == '+':
                    wa_num_list.append(user.whatsapp[1:])
                else:
                    wa_num_list.append(user.whatsapp)
            elif len(user.phone) == 10:
                wa_num_list.append(f'91{user.phone}')
            elif len(user.phone) == 11 and user.phone[0] == '0':
                wa_num_list.append(f'91{user.phone[1:]}')
            elif len(user.phone) == 12 and user.phone[:2] == '91':
                wa_num_list.append(user.phone)
            elif user.phone[:1] == '+':
                wa_num_list.append(user.phone[1:])
            else:
                wa_num_list.append(user.phone)

            name_list.append(user.name.split()[0])

    driver = webdriver.Chrome()
    delay = 35

    for n in range(len(wa_num_list)):
        num = wa_num_list[n]
        message = wa_message
        url = f"https://web.whatsapp.com/send?phone={num}"
        sent = False
        time.sleep(5)
        for i in range(3):
            if not sent:
                driver.get(url)
                try:
                    click_btn = WebDriverWait(driver, delay).until(
                        EC.element_to_be_clickable((By.XPATH, '//*[@id="main"]/footer/div[1]/div/span[2]/div/div[2]/di'
                                                              'v[2]/button/span'))
                    )
                except Exception as e:
                    print(f"Failed to send message to: {num}, retry ({i + 1}/3)....................")
                else:
                    msg_box = driver.find_element(By.XPATH,
                                                  '//*[@id="main"]/footer/div[1]/div/span[2]/div/div[2]/div[1]/div/div[1]/p')

                    msg_box.send_keys(message)
                    sent = True
                    time.sleep(2)
                    print(f'Message sent to: {num} -------- {name_list[n]}')

        if sent:
            if n > 1:
                success_count += 1
    driver.quit()
    print(f"Total receivers to receive message successfully: {success_count}")


def send_wa_msg_by_list(wa_msg, num_list, name_list):
    wa_msg = wa_msg
    num_list = num_list
    name_list = name_list
    wa_num_list = []
    unique_num_list = []

    for n in num_list:
        if len(n) == 10:
            wa_num_list.append(f'91{n}')
        elif len(n) == 11 and n[0] == '0':
            wa_num_list.append(f'91{n[1:]}')
        elif len(n) == 12 and n[:2] == '91':
            wa_num_list.append(n)
        elif n[:1] == '+':
            wa_num_list.append(n[1:])
        else:
            wa_num_list.append(n)

    unique_num_list.insert(0, '918920351265')
    unique_num_list.insert(1, '918920351265')
    name_list.insert(0, 'Test')
    name_list.insert(1, 'Test2')

    for num in wa_num_list:
        if num not in unique_num_list:
            unique_num_list.append(num)

    driver = webdriver.Chrome()
    delay = 35
    success_count = 0
    for n in range(len(unique_num_list)):
        num = unique_num_list[n]
        message = wa_msg.replace("[name]", name_list[n])
        url = f"https://web.whatsapp.com/send?phone={num}"
        sent = False
        time.sleep(5)

        for i in range(3):
            if not sent:
                driver.get(url)
                try:
                    click_btn = WebDriverWait(driver, delay).until(
                        EC.element_to_be_clickable((By.XPATH, '//*[@id="main"]/footer/div[1]/div/span[2]/div/div[2]/di'
                                                              'v[2]/button/span'))
                    )
                except Exception as e:
                    print(f"Failed to send message to: {num}, retry ({i + 1}/3)....................")
                else:
                    msg_box = driver.find_element(By.XPATH,
                                                  '//*[@id="main"]/footer/div[1]/div/span[2]/div/div[2]/div['
                                                  '1]/div/div[1]/p')

                    msg_box.send_keys(message)
                    sent = True
                    time.sleep(2)
                    print(f'Message sent to: {num} -------- {name_list[n]}')

        if sent:
            if n > 1:
                success_count += 1
    driver.quit()
    print(f"Total receivers to receive message successfully: {success_count}")


def send_email_school_and_wa_msg_by_list(subject, recipients, body, html, image_dict, wa_msg, num_list, name_list):
    send_wa_msg_by_list(wa_msg, num_list, name_list)
    send_email_school(subject, recipients, body, html, image_dict)