import sys
import logging
import json
from forward_email import email_created_s3


logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


with open('event.json') as f:
    event = json.load(f)
    email_created_s3(event, None)

