import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from config import EMAIL_PASSWORD

class EmailSender:
    def __init__(self):
        self.sender_email = "daniele96ligato@gmail.com"
        self.app_password = EMAIL_PASSWORD

    def send_email(self, receiver_email, subject, body):
        try:
            message = MIMEMultipart()
            message['From'] = self.sender_email
            message['To'] = receiver_email
            message['Subject'] = subject
            message.attach(MIMEText(body, 'plain'))

            session = smtplib.SMTP('smtp.gmail.com', 587)
            session.starttls()
            session.login(self.sender_email, self.app_password)
            session.sendmail(self.sender_email, receiver_email, message.as_string())
            session.quit()

            print("Email Sent Successfully")
        except Exception as e:
            print(f"Failed to send email: {e}")