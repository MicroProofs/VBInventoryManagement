# Download the helper library from https://www.twilio.com/docs/python/install
from twilio.rest import Client

# Your Account Sid and Auth Token from twilio.com/console
# DANGER! This is insecure. See http://twil.io/secure

def send_message(text, number):

    client = Client(account_sid, auth_token)

    message = client.messages.create(body=text, from_="+12029534376", to=number)

    print(message.sid)
