import smtplib
from email.message import EmailMessage


def send_mail(subject, mail_message):
    sender = 'shwetabh@writart.com'
    password = 'isrgjexqhbjkqftr'

    receiver = 'shwetabhartist@gmail.com'
    message = mail_message
    msg = EmailMessage()
    msg['subject'] = subject
    msg['From'] = sender
    msg['To'] = receiver
    msg.set_content(message)

    with smtplib.SMTP_SSL('smtp.gmail.com') as smtp:
        smtp.login(sender, password)
        smtp.send_message(msg)


send_mail('Test cron job', 'Testing cron job ubuntu user writart')
