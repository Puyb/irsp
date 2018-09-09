from threading import Thread

class MailThread(Thread):
    def __init__ (self, mails):
        Thread.__init__(self)
        self.mails = mails

    def run(self):  
        for mail in self.mails:
            mail.send()
