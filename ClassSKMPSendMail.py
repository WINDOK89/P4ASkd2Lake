from smtplib import *
import email.utils
from email.mime.text import MIMEText


class SKMPSendMail():
    """
    class to send email
    """

    def __init__(self, message="test mail", destination="gilles.bodson@maintenancepartners.com", subject="test message",
                 SmtpServer="smtp.gmail.com", SmtpPort=587, sender="gi.bodson@gmail.com", senderPass="bodgi2011",
                 nameShow="DSE"):
        """
        constructor of the class

        :param message (string): the message we want in the mail body
        :param destination (string): the email where the mail is sent to
        :param subject (string): the subject of the mail
        :param SmtpServer (string): smtp server of the sender
        :param SmtpPort (int): smtp port of the host compurter
        :param sender (string): sender email address
        :param senderPass (string): the sender email accoutn password
        :param nameShow (string): the name to display as senderr in header of receiver mailbox
        :argument result (boolean): false if the mail failed, true otherwise
        """

        #initialize the mail result to true
        self.result = True

        #manage the result via exception + protect main app from crash
        try:

            #mail formatting, look at doc if needed more
            msg = MIMEText(message)
            msg['To'] = email.utils.formataddr(('Recipient', destination))
            msg['From'] = email.utils.formataddr((nameShow, sender))
            msg['Subject'] = subject

            #use of class SMTP (from some stackoverflow findings
            server = SMTP(SmtpServer, SmtpPort)
            server.set_debuglevel(False)
            server.starttls()
            server.login(sender, senderPass)
            try:
                server.sendmail(sender, destination, msg.as_string())
            except:
                self.result=False
            finally:
                server.quit()
        except:
            self.result = False


if __name__ == "__main__":
    if 2 > 1:
        e = SKMPSendMail(nameShow="wintell", message="va  voir le roulement connard",
                         destination="gillesbodson@maintenancepartners.com")
        print(e.result)
