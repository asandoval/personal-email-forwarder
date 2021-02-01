import imaplib
import json
import logging
import os
import boto3


HOST = os.getenv('HOST', 'imap.mail.us-east-1.awsapps.com')
PORT = os.getenv('PORT', 993)
USER = os.getenv('USER', 'anthony@sandov.al')
PASS = os.getenv('PASS')
S3 = boto3.client('s3')

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

conn = imaplib.IMAP4_SSL(host=HOST, port=PORT)
conn.login(USER, PASS)


def s3_message(event, context):
    logger.info(event)
    for record in event['Records']:
        assert record['EventSource'] == 'aws:sns'
        message = json.loads(record['Sns']['Message'], cls=MessageDecoder)
        message.insert(conn)
    conn.logout()


class MessageDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)
    
    def object_hook(self, dct):
        if 'notificationType' in dct:
            mail = dct.get('mail')
            recipients, bucket, key = _decode_receipt(dct.get('receipt'))
            return Message(mail, recipients, bucket, key)
        return dct


def _decode_receipt(receipt):
    recipients = receipt['recipients']
    bucket = receipt['action']['bucketName']
    key = receipt['action']['objectKey']
    return recipients, bucket, key


class Message:
    def __init__(self, mail, recipients, bucket, key):
        self.mail = mail
        self.mailbox = 'Inbox'
        self.flags = None
        self.bucket = bucket
        self.key = key
    
    def raw_mail(self):
        o = S3.get_object(Bucket=self.bucket, Key=self.key)
        raw_mail = o['Body'].read()
        return raw_mail
    
    def insert(self, conn):
        raw_mail = self.raw_mail()
        conn.append(self.mailbox, self.flags, None, raw_mail)

    def _spam(self):
        if self.get('spamVerdict').get('status') != 'PASS':
            self.mailbox = 'Junk'
