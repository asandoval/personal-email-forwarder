import sys
import logging
import json
import mail


logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


with open('tests/sns_message_from_ses.json') as f:
    event = json.load(f)
    mail.created_s3(event, None)

