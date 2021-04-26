from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import logging
import time
import argparse
import json
import requests

ban_users = []

# Custom MQTT message callback
def customCallback(client, userdata, message):
    
    d = json.loads(message.payload)

    print("Received a new message: ", message.payload)
    print("from topic: ", message.topic)
    print("json: ", json.dumps(d))

    for ban in ban_users:
        print(ban)
        if ban == d['publish_id']:
            print ("BAN!!")
            return
    
    text_area.append(d['publish_id'] + " : " + d['message'])

# Setup
parser = argparse.ArgumentParser()
parser.add_argument("-e", "--endpoint", action="store", required=False, dest="host", default="yourIotCoreEndpoint.iot.ap-northeast-2.amazonaws.com", help="Your AWS IoT custom endpoint")
parser.add_argument("-r", "--rootCA", action="store", required=False, default="root-CA.crt", dest="rootCAPath", help="Root CA file path")
parser.add_argument("-c", "--cert", action="store", dest="certificatePath", default="myIoTGameClient.crt" ,help="Certificate file path")
parser.add_argument("-k", "--key", action="store", dest="privateKeyPath", default="myIoTGameClient.key" ,help="Private key file path")
parser.add_argument("-id", "--clientId", action="store", dest="clientId", default="testclient",help="Targeted client id")
parser.add_argument("-t", "--topic", action="store", dest="topic", default="Town137", help="Targeted topic")

args = parser.parse_args()
host = args.host
rootCAPath = args.rootCAPath
certificatePath = args.certificatePath
privateKeyPath = args.privateKeyPath
clientId = args.clientId
topic = args.topic
port = 8883

# Init AWSIoTMQTTClient
myAWSIoTMQTTClient = None

myAWSIoTMQTTClient = AWSIoTMQTTClient(clientId)
myAWSIoTMQTTClient.configureEndpoint(host, port)
myAWSIoTMQTTClient.configureCredentials(rootCAPath, privateKeyPath, certificatePath)

# Connect and subscribe to AWS IoT
myAWSIoTMQTTClient.connect()
publish_topic = "World/Client/" + topic
subscribe_topic = "World/Server/" + topic
myAWSIoTMQTTClient.subscribe(subscribe_topic, 1, customCallback)
print('Conneting IoT Core... : ', subscribe_topic)

seq = 0
        
# GUI:
app = QApplication([])
text_area = QTextEdit()
text_area.setFocusPolicy(Qt.NoFocus)
message = QLineEdit()
layout = QVBoxLayout()
layout.addWidget(text_area)
layout.addWidget(message)
window = QWidget()
window.setLayout(layout)
window.setWindowTitle("AWS Game Chat Service")
window.resize(400,500)
window.show()

# Last messages
resp = requests.get( 'https://yourapigateway-endpoint.execute-api.ap-northeast-2.amazonaws.com/test/get_channel_message/'+ topic)
for last_message in resp.json():

    print(last_message[1])

    #print(last_message[1].strip().replace("b'","").replace("'",""))
    #d = json.loads(last_message[1].strip().replace("b'","").replace("'",""))
    d = json.loads(last_message[1])
    text_area.append(d['publish_id'] + " : " + d['message'])

# Ban users
resp = requests.get( 'https://yourapigateway-endpoint.execute-api.ap-northeast-2.amazonaws.com/test/get_user_info/'+ clientId)
ban_users = resp.json()
for d in resp.json():
    print("ban:" + d)

def send_message():
    global seq
    global ban_users

    iot_send = {}
    iot_send['publish_id'] = clientId
    iot_send['message'] = message.text()
    iot_send['sequence'] = seq
    iot_send['channel'] = topic
    
    if message.text().startswith('/ban '):
        ban_target = message.text().split(" ")[1]
        print("ban!:" + ban_target)
        ban_users.append(ban_target)
        for b in ban_users:
            print(b)

    messageJson = json.dumps(iot_send)
    print("send:" + messageJson)
    myAWSIoTMQTTClient.publish(publish_topic, messageJson, 1)
    
    message.clear()
    seq += 1

# Signals:
message.returnPressed.connect(send_message)
app.exec_()
        
