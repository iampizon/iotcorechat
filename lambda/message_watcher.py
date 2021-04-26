from __future__ import print_function
import json
import base64
import boto3
import redis
import os
import logging
import jsonpickle
from datetime import datetime
import time
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch_all

patch_all()

redis_conn = redis.StrictRedis(host='yourredis-endpoint.amazonaws.com', port=6379, db=0)
iot_conn = boto3.client('iot-data')
ddb_conn = boto3.resource("dynamodb", region_name='ap-northeast-2', endpoint_url="http://dynamodb.ap-northeast-2.amazonaws.com")
ddb_table = ddb_conn.Table('IoTChat')
ddb_user_table = ddb_conn.Table('IoTChatUsers')

def lambda_handler(event, context):
    # Parse the JSON message 

    eventText_orinal = json.dumps(event)

    # Parse commands
    if event['message'].startswith('/ban '):
        commands = event['message'].split(' ')
        print("target_user:" + event['publish_id'] + "->" + commands[1])
        
        try :
           response = ddb_user_table.put_item(
                Item = {'userid':event['publish_id'],'blockids':[commands[1]]},
                ConditionExpression = "attribute_not_exists(userid)"
            )
        except :
            response = ddb_user_table.update_item(
                    Key = {'userid':event['publish_id']},
                    UpdateExpression="SET blockids[1000] = :val1",
                    ExpressionAttributeValues={":val1" : commands[1]} 
                )

        # Stop processing
        return
    
    # Filter bad words   
    ddb_response = ddb_table.get_item(Key={"key":"bad-words"})
    ddb_item = ddb_response['Item']
    for bad_word in ddb_item['value']:
        event['message'] = event['message'].replace(bad_word, "****")

    eventText = json.dumps(event)

    # Generate redis key
    (dt, micro) = datetime.utcnow().strftime('%Y%m%d%H%M%S.%f').split('.')
    dt = "%s%03d" % (dt, int(micro) / 1000)

    channel = event['channel'];
    sub_topic = 'World/Server/' + channel
    redis_key = channel +":"+ dt

    # Publish to IoT!
    iot_conn.publish(topic=sub_topic, qos=1, payload=eventText)
      
    redis_conn.set(redis_key, eventText_orinal)
    redis_conn.expire(redis_key, 30)
    data = redis_conn.get(redis_key)

    time.sleep(1)

    return
