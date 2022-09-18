import random
from twilio.rest import Client


def getOTPApi(number, otp):
    account_sid = "ACcc6898d7d8eb5909488598cc828f3d2f"
    auth_token = "950701e1e9c6dc3814e4f960e0708df1"
    client = Client(account_sid, auth_token)
    body = "Your OTP for MedBase is "+str(otp)
    message = client.messages.create(
        body=body,
        from_='+19786724918',
        to=f'+91{number}'
    )

    if message.sid:
        return True
    else:
        return False
