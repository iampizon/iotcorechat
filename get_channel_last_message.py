from __future__ import print_function
import json
import base64
import boto3
import redis
import logging
import jsonpickle
from datetime import datetime
from collections import OrderedDict
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch_all

patch_all()

redis_conn = redis.StrictRedis(host='yourredis-endpoint.amazonaws.com', port=6379, db=0)
ddb_conn = boto3.resource("dynamodb", region_name='ap-northeast-2', endpoint_url="http://dynamodb.ap-northeast-2.amazonaws.com")
ddb_table = ddb_conn.Table('IoTChat')

def lambda_handler(event, context):
    # Parse the JSON message 
    eventText = json.dumps(event)
  
    print('Received event: ', eventText)
    
    ddb_response = ddb_table.get_item(Key={"key":"bad-words"})
    ddb_item = ddb_response['Item']

    #channel = event['channel']
    channel= event['pathParameters']['channel']
    match_key = channel + '*'
    print(match_key)
    return_data = {}
    
    for redis_key in redis_conn.scan_iter(match=match_key, count=100):
        print(redis_key)
        
        data = redis_conn.get(redis_key)
        
        key_str = redis_key.decode('utf-8')
        data_str = data.decode('utf-8')
        
        data_json = json.loads(data_str)
        #print("data_json=" + data_json)
        for bad_word in ddb_item['value']:
            data_json['message'] = data_json['message'].replace(bad_word, "****")

        data_str = json.dumps(data_json)
        return_data[key_str] = data_str
        if len(return_data) >= 30:
            break
        
    print(return_data)
    return_data = sorted(return_data.items())
    
    return {
        "statusCode": 200,
        #"body": path_param
        "body": json.dumps(return_data)
    }
