from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import logging
import time
import argparse
import json
import requests
from datetime import datetime
import random
from random import randint

message_box = ['Hey', 'Hello guys~' , 'How are you?', 'I am fine, Thank you and you?' , 'I love you', 'I gotta go hospital',
'LOL', '=)','^^','T_T',':)))))))))))','@_@;;;;;;;;;;;;', 'Ohhh....^^^^', 'heeeyyy...', 'sup??','@_@!','kewl....','kkkkk...','haha yumyum', 'Is it true!?', 'What the c8', 'babo ya', 'hmmmm.....', 'Nope', 'Okay....', 'I got it', 'Do you have a book?','no no no... it cannot be',
'ah ha!', 'BINGO!!', 'ooooops', 'What time is it now?', 'how many things...', 'Yes, Of course~~~~', 'yeah, my bro', 'Sure, I am a superstar','Good job']

message_box2 = [
'Hey', 'HELLO GUYS!!' , 
'Miracles happen to only those who believe in them.',
'Think like a man of action and act like man of thought.',
'Courage is very important. Like a muscle, it is strengthened by use.   ',
'Life is the art of drawing sufficient conclusions from insufficient premises.  ',
'By doubting we come at the truth. ',
'A man that has no virtue in himself, ever envies virtue in others. ',
'When money speaks, the truth keeps silent.',
'Better the last smile than the first laughter.',
'In the morning of life, work; in the midday, give counsel; in the evening, pray. ',
'Painless poverty is better than embittered wealth.',
'A poet is the painter of the soul.',
'Error is the discipline through which we advance. ',
'Faith without deeds is useless.   ',
'Weak things united become strong. ',
'We give advice, but we cannot give conduct. ',
'Nature never deceives us; it is always we who deceive ourselves. ',
'Forgiveness is better than revenge. ',
'We never know the worth of water till the well is dry.',
'Pain past is pleasure.',
'Books are ships which pass through the vast seas of time.  ',
'Who begins too much accomplishes little.  ',
'Better the last smile than the first laughter.',
'Faith is a higher faculty than reason.',
'Until the day of his death, no man can be sure of his courage. ',
'Great art is an instant arrested in eternity. ',
'Faith without deeds is useless.   ',
'The world is a beautiful book, but of little use to him who cannot read it.',
'Heaven gives its favorites-early death.',
'I never think of the future. It comes soon enough.',
'Suspicion follows close on mistrust.  ',
'He who spares the rod hates his son, but he who loves him is careful to discipline him.',
'All good things which exist are the fruits of originality. ',
'The will of a man is his happiness.   ',
'He that has no shame has no conscience.',
'Weak things united become strong. ',
'United we stand, divided we fall. ',
'To doubt is safer than to be secure.  ',
'Time is but the stream I go a-fishing in. ',
'A full belly is the mother of all evil.',
'Love your neighbor as yourself.   ',
'It is a wise father that knows his own child. ',
'By doubting we come at the truth. ',
'Absence makes the heart grow fonder.  ',
'Habit is second nature.',
'Who knows much believes the less. ',
'Only the just man enjoys peace of mind.',
'Waste not fresh tears over old griefs.',
'Life itself is a quotation. ',
'Envy and wrath shorten the life.  ',
'Where there is no desire, there will be no industry.  ',
'To be trusted is a greater compliment than to be loved.',
'Education is the best provision for old age.  ',
'To jaw-jaw is better than to war-war. ',
'Appearances are deceptive.',
'Let thy speech be short, comprehending much in few words.  ',
'Things are always at their best in the beginning. ',
'A gift in season is a double favor to the needy.  ',
'In giving advice, seek to help, not to please, your friend.',
'The difficulty in life is the choice. ',
'The most beautiful thing in the world is, of course, the world itself. ',
'All fortune is to be conquered by bearing it. ',
'Better is to bow than break.  ',
'Good fences makes good neighbors. ',
'Give me liberty, or give me death.'
]

def current_time():
    (dt, micro) = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f').split('.')
    dt = "%s%03d" % (dt, int(micro) / 1000)
    return dt


# Custom MQTT message callback
def customCallback(client, userdata, message):
    
    d = json.loads(message.payload)
#    if d["publish_id"] != clientId :

    print(message.topic + " Recv : " , message.payload , ":" , current_time()  )

#default client id
(dt, micro) = datetime.utcnow().strftime('%M%S.%f').split('.')
dt = "%s%03d" % (dt, int(micro) / 1000)
default_client_id = "BOT-"+dt

default_join_channel = "Town" + str(randint(100,200))

parser = argparse.ArgumentParser()
parser.add_argument("-e", "--endpoint", action="store", required=False, dest="host", default="youriotcore-endpoint.iot.ap-northeast-2.amazonaws.com", help="Your AWS IoT custom endpoint")
parser.add_argument("-r", "--rootCA", action="store", required=False, default="root-CA.crt", dest="rootCAPath", help="Root CA file path")
parser.add_argument("-c", "--cert", action="store", dest="certificatePath", default="myIoTGameClient.crt" ,help="Certificate file path")
parser.add_argument("-k", "--key", action="store", dest="privateKeyPath", default="myIoTGameClient.key" ,help="Private key file path")
parser.add_argument("-id", "--clientId", action="store", dest="clientId", default=default_client_id, help="Targeted client id")
parser.add_argument("-t", "--topic", action="store", dest="topic", default=default_join_channel, help="Targeted topic")

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

# AWSIoTMQTTClient connection configuration
myAWSIoTMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
myAWSIoTMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
myAWSIoTMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
myAWSIoTMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
myAWSIoTMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec

# Connect and subscribe to AWS IoT

print('Waiting...') 
time.sleep(random.uniform(1,20))

myAWSIoTMQTTClient.connect()
publish_topic = "World/Client/" + topic
subscribe_topic = "World/Server/" + topic
#subscribe_topic = topic 
myAWSIoTMQTTClient.subscribe(subscribe_topic, 1, customCallback)
print('Conneting IoT Core... : ', subscribe_topic)

seq = 0
        

while True:
    iot_send = {}
    iot_send['publish_id'] = clientId

    if clientId[10] == '0':
        iot_send['message'] = random.choice(message_box2)
    else:
        iot_send['message'] = random.choice(message_box)

    iot_send['sequence'] = seq
    iot_send['channel'] = topic

    messageJson = json.dumps(iot_send)
    print(publish_topic + " Send :" , messageJson , ":" , current_time() )
    myAWSIoTMQTTClient.publish(publish_topic, messageJson, 1)

    seq += 1

    time.sleep(random.uniform(0,3))
   

