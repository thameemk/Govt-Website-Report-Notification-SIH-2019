import sendgrid
import os
from sendgrid.helpers.mail import *

sg = sendgrid.SendGridAPIClient(apikey='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')
from_email = Email("isro@gov.in")
to_email = Email("irene.tenison@gmail.com")
subject = "Job Offer"
content = Content("text/plain", "Your job application is accepted \ We will notify the further procedure")
mail = Mail(from_email, subject, to_email, content)
response = sg.client.mail.send.post(request_body=mail.get())
print(response.status_code)
print(response.body)
print(response.headers) 
