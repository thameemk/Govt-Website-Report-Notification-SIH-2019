import sendgrid
import os
from sendgrid.helpers.mail import *

sg = sendgrid.SendGridAPIClient(apikey='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')
from_email = Email("isro@gov.in")
list = ["thameemk612@yahoo.com","irene.tenison@gmail.com"]
for i in range (len(list)):
    to_email = Email(list[i])
    subject = "Job Offer"
    content = Content("text/plain", "Your job application is accepted \ We will notify the further procedure")
    mail = Mail(from_email, subject, to_email, content)
    response = sg.client.mail.send.post(request_body=mail.get())
print(response.status_code)

