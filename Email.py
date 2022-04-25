import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

class EmailClass():

    def __init__(self, receiver_address):
        mail_content = '''Hello Manager,
This is a message to inform you that one of our cameras has caught a suspicious activity.
Please check the camera and take appropriate action.

Thanks,
Security Team.'''

        #The mail addresses and password
        sender_address = 'PythonCameraAlert@gmail.com'
        sender_pass = 'ALERTWASFOUND'
        # receiver_address = 'Noamiko.tirosh3@gmail.com'

        #Setup the MIME
        message = MIMEMultipart()
        message['From'] = sender_address
        message['To'] = receiver_address
        message['Subject'] = '!!! ALERT !!! INTRUDER FOUND'

        #The subject line
        #The body and the attachments for the mail
        message.attach(MIMEText(mail_content, 'plain'))
        attach_file_name = "NoamCamLogo.png"
        attach_file = open(attach_file_name, 'rb') # Open the file as binary mode
        payload = MIMEBase('application', 'octate-stream')
        payload.set_payload((attach_file).read())
        encoders.encode_base64(payload) #encode the attachment
        #add payload header with filename
        payload.add_header('Content-Decomposition', 'attachment', filename=attach_file_name)
        message.attach(payload)
        #Create SMTP session for sending the mail
        session = smtplib.SMTP('smtp.gmail.com', 587) #use gmail with port
        session.starttls() #enable security
        session.login(sender_address, sender_pass) #login with mail_id and password
        text = message.as_string()
        session.sendmail(sender_address, receiver_address, text)
        session.quit()
        print('Mail Sent')

if __name__ == '__main__':
    EmailClass("Noamiko.tirosh3@gmail.com")