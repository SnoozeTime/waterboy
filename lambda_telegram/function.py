import json
import os
import datetime
import pytz
from botocore.vendored import requests


import boto3
dynamodb = boto3.resource('dynamodb')

TOKEN =  os.environ['TELEGRAM_TOKEN']
URL = f'https://api.telegram.org/bot{TOKEN}/sendMessage'

def get_allowed_users():
    liststr = os.environ['ALLOWED_USERS']
    return [int(x) for x in liststr.split(',')]

# This is a workaround for: http://bugs.python.org/issue16535
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return int(obj)
        return super(DecimalEncoder, self).default(obj)


def create_entry(dt: str):
    """ Will create a new entry in the dynamotable. Key will be the current
    datetime"""
    table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])
    item = {
        'datetime': dt,
        'request': 'Please water my plants',
    }
    table.put_item(Item=item)


def send_msg(chat_id, msg):
    r = requests.post(URL, data={'chat_id': chat_id, 'text': msg})
    print(r.text)

def lambda_handler(event, context):

    body = json.loads(event['body'])

    # Process only if myself 
    user_id = body['message']['from']['id']
    if user_id in get_allowed_users():
        text = body['message']['text']
        chat_id = body['message']['chat']['id']
        if text.startswith('/water'):
            now = datetime.datetime.now()
            tz = pytz.timezone('Asia/Tokyo')
            now = tz.localize(now)
            create_entry(now.isoformat())
            msg = f"OK I RECEIVED YOUR REQUEST AT {now.isoformat()}"
        else:
            msg = 'Type /water to water the plants'
        send_msg(chat_id, msg)

    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }

