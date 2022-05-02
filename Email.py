import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from os.path import basename


class EmailClass():

    def __init__(self, sender, sender_pas):

        self.sender_address = sender
        self.sender_pass = sender_pas
        self.message = MIMEMultipart()
        # self.files = files
        # self.receiver_address = receiver_address


    def _build_base_message(self, to_address):


        #The mail addresses and password
        sender_address = 'PythonCameraAlert@gmail.com'
        sender_pass = 'ALERTWASFOUND'
        # receiver_address = 'Noamiko.tirosh3@gmail.com'

        #Setup the MIME
        self.message['From'] = sender_address
        self.message['To'] = to_address
        self.message['Subject'] = '!!! ALERT !!! INTRUDER FOUND'


    def _build_attachment(self, file_path):


        mail_content = '''Hello Manager,
This is a message to inform you that one of our cameras has caught a suspicious activity.
Please check the camera and take appropriate action.

Thanks,
Security Team.'''

        self.message.attach(MIMEText(mail_content))

        with open(file_path, "rb") as fil:
            part = MIMEApplication(
                fil.read(),
                Name=basename(file_path)
                )
        # After the file is closed
        part['Content-Disposition'] = 'attachment; filename="%s"' % basename(file_path)
        self.message.attach(part)



    def send_mail(self, image_path, to_address):
        self.message = MIMEMultipart()
        self._build_base_message(to_address)
        self._build_attachment(image_path)
        # #Create SMTP session for sending the mail
        session = smtplib.SMTP('smtp.gmail.com', 587) #use gmail with port
        session.starttls() #enable security
        session.login(self.sender_address, self.sender_pass) #login with mail_id and password
        # text = message.as_string()
        session.sendmail(self.sender_address, to_address, self.message.as_string())
        session.quit()
        print('Mail Sent')



if __name__ == '__main__':
    # EmailClass("Noamiko.tirosh3@gmail.com")
    x = EmailClass('PythonCameraAlert@gmail.com', 'ALERTWASFOUND')
    x.send_mail("Try.txt", "Noamiko.tirosh3@gmail.com")