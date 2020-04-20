import imaplib
import json
import logging
import os
import boto3


HOST = os.getenv('HOST', 'imap.mail.us-east-1.awsapps.com')
PORT = os.getenv('PORT', 993)
USER = os.getenv('USER', 'anthony@sdval.com')
PASS = os.getenv('PASS')
S3 = boto3.client('s3')

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def email_created_s3(event, context):
    logger.info(event)
    for record in event['Records']:
        assert record['EventSource'] == 'aws:sns'
        msg = json.loads(record['Sns']['Message'])
        logger.info("Message received from SNS: {}".format(msg))
        receipt = msg['receipt']
        spam = receipt['spamVerdict']['status']
        mailbox = 'Inbox'
        flags = None
        if spam != 'PASS':
            mailbox = 'Junk'
        if 'anthony@sdval.com' in receipt['recipients']:
            continue
        action = receipt['action']
        bucket = action['bucketName']
        key = action['objectKey']
        o = S3.get_object(Bucket=bucket, Key=key)
        raw_mail = o['Body'].read()
        logger.info("body: {}".format(type(raw_mail)))
        M = imaplib.IMAP4_SSL(host=HOST, port=PORT)
        M.login(USER, PASS)
        M.append(mailbox, flags, None, raw_mail)
        M.logout()
