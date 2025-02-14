import email.header
import email.mime.text
import smtplib

from settings import SEND_RESULT_MAIL, SMTP_USER, SMTP_PASSWORD, SMTP_HOST


def send_mail(text=""):
    if not SEND_RESULT_MAIL:
        return
    msg = email.mime.text.MIMEText(text)
    me = 'dev@aerooffers.pl'
    msg['Subject'] = 'Aircraft Offers Crawling Result'
    msg['From'] = SMTP_USER
    msg['To'] = me

    server = smtplib.SMTP_SSL(SMTP_HOST, 465)
    server.login(SMTP_USER, SMTP_PASSWORD)
    server.sendmail(me, [me], msg.as_string())
    server.quit()


if __name__ == '__main__':
    send_mail("testmail")
