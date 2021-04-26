from __future__ import print_function
import json
import base64
import boto3
import redis
from datetime import datetime
from collections import OrderedDict

ddb_conn = boto3.resource("dynamodb", region_name='ap-northeast-2', endpoint_url="http://dynamodb.ap-northeast-2.amazonaws.com")
ddb_user_table = ddb_conn.Table('IoTChatUsers')

def lambda_handler(event, context):
    # Parse the JSON message 
    eventText = json.dumps(event)
    userid= event['pathParameters']['userid']
    print('Received event: ', eventText)
    
    try:
        ddb_response = ddb_user_table.get_item(Key={"userid":userid})
        ddb_item = ddb_response['Item']
        
        print(ddb_item)
        
        return_data = json.dumps(ddb_item['blockids'])

    except:
        return_data = json.dumps([])

    return {
        "statusCode": 200,
        "body": return_data
    }
