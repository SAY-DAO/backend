from mailerlite import MailerLiteApi

from say.config import config

mailerlite = MailerLiteApi(config.get('MAILERLITE_API_KEY', 'not-entered'))