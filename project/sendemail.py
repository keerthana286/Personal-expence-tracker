import sendgrid
import os
from sendgrid.helpers.mail import Mail, Email, To, Content

def sendgridmail(user,TEXT):
    sg = sendgrid.SendGridAPIClient('''<Change to your API key>''')
    from_email = Email("Expenses Tracker <'''your mail id'''>") # Change to your verified sender
    to_email = To(user)  # Change to your recipient
    subject = "Personal Expense Tracker"
    content = Content("text/plain",TEXT)
    try:
        mail = Mail(from_email, to_email, subject, content)
        # Get a JSON-ready representation of the Mail object
        mail_json = mail.get()
        # Send an HTTP POST request to /mail/send
        response = sg.client.mail.send.post(request_body=mail_json)
        return 1
    except Exception as e:
        return 0
    

