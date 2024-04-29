from django.conf import settings

from twilio.rest import Client

twilio_client = Client(
    settings.TWILIO_ACCOUNT_SID,
    settings.TWILIO_AUTH_TOKEN,
)


class SMSNotification:
    """Provide logic to send sms via Twilio."""

    def __init__(self):
        self.client = twilio_client
        self.message = None

    def get_body(self):
        """Get the body of the message."""
        raise NotImplementedError()

    def get_to_number(self):
        """Get to phone number."""
        raise NotImplementedError()

    def get_from_number(self):
        """Get from phone number."""
        return settings.TWILIO_PHONE_NUMBER

    def send(self):
        """Send sms via Twilio."""
        self.message = self.client.messages.create(
            body=self.get_body(),
            from_=self.get_from_number(),
            to=self.get_to_number(),
        )
