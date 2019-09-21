import json
import boto3
import json
import decimal
from boto3.dynamodb.conditions import Key, Attr

dynamodb = boto3.resource('dynamodb')

# Helper class to convert a DynamoDB item to JSON.
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)


def lambda_handler(event, context):
    table = dynamodb.Table('waterboy')
    response = table.scan()

    # could have some problem? I guess. Anyway nobody else is reading/updating these values.
    for r in response['Items']:
        table.delete_item(Key={'datetime': r['datetime']})

    print(response)

    return {
        'statusCode': 200,
        'body': json.dumps({'items': response['Items']})
    }

