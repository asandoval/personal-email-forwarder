import sys
import logging
import json
from lambda import email_created_s3


logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


with open('tests/sns_message_from_ses.json') as f:
    event = json.load(f)
    email_created_s3(event, None)

