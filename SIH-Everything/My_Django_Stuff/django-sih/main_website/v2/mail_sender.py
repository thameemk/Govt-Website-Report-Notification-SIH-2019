import sendgrid
import os
from sendgrid.helpers.mail import *
from urllib.request import urlretrieve
import os

import base64

def sendMailMultiple(pdf_url, pdf_name):
    print("Sending mail!")
    sg = sendgrid.SendGridAPIClient(apikey='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')

    from_email = Email("demo@coding_panda.com")
    list = ["thameemk612@yahoo.com", "irene.tenison@gmail.com"]

    for i in range(len(list)):
        to_email = Email(list[i])
        subject = "New Report: {pdf_name}".format(pdf_name=pdf_name)
        mail_content = "A new publication {pdf_name} has been published.\n\nHappily,\nCoding Panda :)".format(
            pdf_name=pdf_name)
        content = Content("text/plain", str(mail_content))

        file_path = '{pdf_name}.pdf'.format(pdf_name=pdf_name)
        urlretrieve(pdf_url, file_path)

        # file_path = '/Users/sreekant/Desktop/sweet/Japan_EngineeringServices_PPT.pdf'
        with open(file_path, 'rb') as f:
            data = f.read()
            f.close()
        encoded = base64.b64encode(data).decode()

        attachment = Attachment()
        attachment.content = encoded
        attachment.type = "application/pdf"
        attachment.filename = pdf_name
        attachment.disposition = "attachment"
        attachment.content_id = "Example Content ID"

        mail = Mail(from_email, subject, to_email, content)
        mail.add_attachment(attachment)

        try:
            response = sg.client.mail.send.post(request_body=mail.get())
        except urllib.HTTPError as e:
            print(e.read())
            exit()

    if (response.status_code == 202):
        os.remove("{pdf_name}.pdf".format(pdf_name=pdf_name))
        print("Mail sent succesfully!")
