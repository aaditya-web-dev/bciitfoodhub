from twilio.rest import Client
import os

def send_sms(phone, message):
    client = Client(
        os.getenv("TWILIO_SID"),
        os.getenv("TWILIO_AUTH_TOKEN")
    )

    # 🔥 CLEAN & FORMAT PHONE
    phone = str(phone).strip()
    phone = phone.replace(" ", "").replace("-", "")

    # remove country code if already present
    if phone.startswith("+91"):
        phone = phone[3:]
    elif phone.startswith("91"):
        phone = phone[2:]

    # final correct format
    phone = "+91" + phone

    print("FINAL PHONE:", phone)   # 🔍 debug

    message = client.messages.create(
        body=message,
        from_=os.getenv("TWILIO_PHONE"),
        to=phone
    )

    print("SMS SENT:", message.sid)