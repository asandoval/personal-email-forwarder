import imaplib
import json
import logging
import os
import boto3
from dotenv import load_dotenv


load_dotenv()


HOST = os.getenv('HOST', 'imap.mail.us-east-1.awsapps.com')
PORT = os.getenv('PORT', 993)
USER = os.getenv('USER', 'anthony@sandov.al')
PASS = os.getenv('PASS')
S3 = boto3.client('s3')

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

conn = imaplib.IMAP4_SSL(host=HOST, port=PORT)
conn.login(USER, PASS)


def created_s3(event, context):
    logger.info(event)
    for record in event['Records']:
        assert record['EventSource'] == 'aws:sns'
        mail = json.loads(record['Sns']['Message'], object_hook=mail_decoder)
        mail.insert(conn)
    conn.logout()


def mail_decoder(msg):
    logger.info("Message received from SNS: {}".format(msg))
    return Mail(msg)


class Mail:

    def __init__(self, msg):
        self.msg = msg
        self.mailbox = 'Inbox'
        self.flags = None

    @property
    def receipt(self):
        return self.msg.get('receipt')

    def spam(self):
        if self.receipt.get('spamVerdict').get('status') != 'PASS':
            self.mailbox = 'Junk'
    
    def raw_mail(self):
        action = self.receipt.get('action')
        bucket = action.get('bucketName')
        key = action.get('objectKey')
        o = S3.get_object(Bucket=bucket, Key=key)
        raw_mail = o['Body'].read()
        return raw_mail

    def insert(self, conn):
        conn.append(self.mailbox, self.flags, None, self.raw_mail())
