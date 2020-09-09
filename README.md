# Build Chat Service with AWS IoT Core

게임 개발 초기에는 게임성을 결정하는 아키텍처와 콘텐츠 개발에 신경을 쓰기 마련입니다. 그러다 보면 모든 게임의 공통 요소인 채팅, 상점, 이벤트 같은 시스템은 우선순위가 밀려서 부랴부랴 출시 전에 개발에 착수하게 됩니다. 하지만 이런 시스템들도 대규모 멀티플레이 환경을 위해서 고려해야 할 요소들이 많습니다. 기본 기능 외에도 분산과 확장 가능한 구조가 필요하고, 재해 복구와 모니터링이 가능해야 하기 때문입니다.

신규 게임을 만들 때마다 매번 개발해야 하는 이런 시스템에 마이크로서비스 (https://aws.amazon.com/ko/microservices)아키텍처를 적용하고, AWS의 서버리스 (http://aws.amazon.com/ko/serverless)서비스를 활용하면 여러 이점이 있습니다. 이 글에서는 게임 채팅 서비스를 AWS IoT Core를 활용하여 구현해보고, 어떤 이점이 있는지 살펴보겠습니다.


1. AWS IoT Core 소개

AWS IoT Core (https://aws.amazon.com/ko/iot-core)는 서비스명에서도 알 수 있듯이 IoT(사물인터넷) 지원을 위해 개발된 서비스로 다음과 같은 특징을 가지고 있습니다.


* 수십억 개의 디바이스가 접속하여 수조 개의 메시지를 주고받을 수 있도록 설계됐습니다.
* AWS 완전 관리형으로, 부하 분산, 리소스 확장 및 축소 같은 인프라 관리에 신경 쓸 필요가 없습니다.
* 메시지 브로커 서비스입니다. 접속한 디바이스가 경량화된 프로토콜인 MQTT (https://docs.aws.amazon.com/ko_kr/iot/latest/developerguide/mqtt.html)를 사용하여 빠르고 안정적으로 메시지를 주고받을 수 있습니다.


냉장고, TV 같은 디바이스를 위해 개발된 사물인터넷 서비스로 게임 내 채팅을 구현한다면 의아할 수 있을 것 같습니다. 하지만 AWS IoT Core의 디바이스용 SDK는 embedded-C 언어뿐 아니라, Python, Java, C++ 도 지원하며, 모바일 게임에서 활용할 수 있는 Android, iOS 버전도 함께 제공합니다. 게다가 Pub/Sub 모델로 구현된 메세지 브로커 서비스는 주제별(Topic)로 게시자(Publisher)와 구독자(Subscriber)가 메시지를 주고받을 수 있기 때문에 채팅 서비스에 매우 적합한 아키텍처입니다.

AWS에서 제공하는 또 다른 메시지 브로커 서비스는 Amazon MQ (https://aws.amazon.com/ko/amazon-mq), Amazon Managed Streaming for Apache Kafka (https://aws.amazon.com/ko/msk)(이하 MSK), Amazon Simple Queue Service (https://aws.amazon.com/ko/sqs)(이하 SQS) 등이 있습니다. Amazon MQ, Amazon MSK는 각각 Apache ActiveMQ와 Apache Kafka 오픈소스를 기반으로 제공하는 서비스입니다. 기존에 이런 컴포넌트를 사용하고 있다면 고려해 볼 수 있는데, 인프라 관리 측면에서 AWS가 제공하는 완전 관리형 서비스보다 리소스 분산과 확장에 손이 많이 갑니다. Amazon SQS 역시 완전 관리형 메시지 브로커 서비스지만, 메시지 큐잉에 초점이 맞추어진 서비스로 다른 애플리케이션과 연동하여 마이크로서비스를 구축하는 데 유용합니다.


*2. AWS IoT Core 로 채널 기반 채팅 구현하기*

일반적인 게임에서 채팅은 채널을 기반으로 이루어집니다. 특정한 서버나 필드마다 여러 개의 채널을 생성해두고, 사용자들은 필요에 따라 채널을 이동하면서 해당 채널 안에 있는 다른 사용자와 대화를 나눌 수 있습니다. 이를 AWS IoT Core의 메시지 브로커 아키텍처에 대응하면, AWS IoT Core의 주제를 게임 내 하나의 채널로 산정 할 수 있습니다. 사용자가 특정 채널에 접속하면, 해당하는 주제의 게시자와 구독자로 등록합니다. 메시지를 보낼 때는 해당 주제로 게시하고, 다른 사용자의 메시지는 구독하여 받아 볼 수 있는 것입니다.

AWS IoT Core 로 구성한 채팅 서비스 아키텍처를 살펴보겠습니다.



[Image: iotchat.png]

각각의 게임 클라이언트가 AWS IoT Core의 “Town137” 이라는 주제를 구독, 게시하도록 구성했습니다. 게임상에서 137번 마을에 입장 했을 때 접속하는 채널이라고 가정했습니다. Town138, Town139... 등의 원하는 이름으로, 필요한 만큼 주제(채널)를 생성할 수도 있습니다.  

이런 주제의 생성과 삭제, 게시자 및 구독자 등록을 AWS IoT Core에서 제공하는 SDK를 사용하여 손쉽게 할 수 있습니다. 기능별로 권한을 설정하여, 사용자들이 편의에 따라 채널을 생성/삭제하도록 허용하거나, 관리자(운영툴이나 게임서버에서)만 가능하도록 제한 할 수도 있습니다.  또한, AWS IoT Core는 완전 관리형 서비스로 부하 분산과 리소스 확장에 신경 쓸 필요가 없고, 이런 구성만으로 대규모 접속자의 채팅방 개설과 메시지 송수신이 가능합니다. 

AWS IoT Core의 SDK로 구현한 게임 클라이언트의 채널 생성 코드를 살펴보겠습니다.

#Init AWSIoTMQTTClient
myAWSIoTMQTTClient = AWSIoTMQTTClient(client_id)
myAWSIoTMQTTClient.configureEndpoint(host, port)

#Connect and subscribe to AWS IoT
myAWSIoTMQTTClient.connect()

topic = "Town" + game_channal_number

myAWSIoTMQTTClient.subscribe(topic, 1, recv_message_callback)

Python으로 구현한 코드 예시입니다. AWS IoT Core의 엔드포인트로 접속한 뒤, 사용자가 설정한 주제를 구독했습니다. 사용자가 채널을 생성 할 수 있도록 권한을 설정한 상태이기 때문에, 해당 이름의 주제가 없다면 자동으로 생성됩니다. 이제 메시지를 주고 받는 코드를 살펴보겠습니다.

def send_message():
    message = {}
    message['publish_id'] = client_id
    message['message'] = ui_message.text()
    message['channel'] = game_channal_number
    
    message_json = json.dumps(message)
    myAWSIoTMQTTClient.publish(topic, message_json , 1)
    
    ui_message.clear()
    
def recv_message_callback(client, userdata, message):
    d = json.loads(message.payload)
    ui_text_area.append(d['publish_id'] + " : " + d['message'])    

send_message 함수는 게시자 ID 와 메시지, 채널명의 정보가 담긴 JSON 형태의 메시지를 생성하여 AWS IoT Core로 게시합니다. recv_message_callback은 메시지를 수신하면 호출되는 콜백 함수입니다. 간단히 메시지 내용을 클라이언트의 UI 에 출력하도록 구현했습니다. 이렇게 코드 몇 줄만으로 채팅 메시지 송수신 기능 구현이 완료됐습니다. 이 메시지들은 모두 암호화되어 전송되며, 암복호화 루틴은 AWS의 SDK 내부에 구현돼있습니다.


*3. 지난 대화 보기 기능 구현하기*


채널을 생성하고, 사용자 간 메시지를 주고받는 것으로 채팅의 기본 기능은 완성이 됐습니다. AWS IoT Core를 사용하므로 채팅 서비스 구현의 가장 어려운 부분인 대규모 사용자의 접속 관리와 메시지 처리는 걱정하지 않아도 됩니다. 하지만, 게임 내 채팅에는 몇 가지 추가 기능이 필요합니다. 그중에서 ‘지난 대화 보기’ 기능은 반드시 서버에 데이터를 저장해야 하는데, 이를 AWS Lambda (https://aws.amazon.com/ko/lambda)와 Amazon API Gateway (https://aws.amazon.com/ko/api-gateway), Amazon ElastiCache (https://aws.amazon.com/ko/elasticache) 서비스를 활용하면 손쉬운 구성이 가능합니다.

다음은 ‘지난 대화 보기’ 기능을 위해 AWS IoT Core 채팅 서비스를 확장한 아키텍처입니다.
[Image: iot-chat.png]AWS IoT Core와 다른 AWS 서비스 간의 연동은 클릭 몇 번만으로 가능합니다. 이 아키텍처에서 AWS IoT Core와 AWS Lambda를 연동하여, AWS IoT Core로 수신되는 모든 메시지를 Lambda 함수에서 필터링하도록 구현했습니다. MessageFilter Lambda 함수는 수신한 메시지를 채널별로 모두 Amazon ElastiCache에 30초의 TTL을 주고 저장하도록 합니다. 이 후, 사용자가 채널에 접속했을 때, Amazon API Gateway로 지난 대화 보기 Lambda 함수인 GetLastMessage를 호출합니다. 이 함수는 ElastiCache에 저장돼있는 해당 채널의 최근 30초간 대화 내용을 반환합니다. 클라이언트에서 이 내용을 화면에 출력하도록 구현하면 기능이 완성됩니다.

먼저 MessageFilter Lambda 함수의 코드를 살펴보겠습니다.

import json
import base64
import boto3
import redis
from datetime import datetime

redis_conn = redis.StrictRedis(
    host='iotchatcache.xxx.ng.0001.apn2.cache.amazonaws.com', port=6379, db=0)

def lambda_handler(event, context):
    received_message = json.dumps(event)
    
    # Generate redis unique-key
    (dt, micro) = datetime.utcnow().strftime('%Y%m%d%H%M%S.%f').split('.')
    dt = "%s%03d" % (dt, int(micro) / 1000)
    
    channel = event['channel'];
    redis_key = channel +":"+ dt
    
    redis_conn.set(redis_key, received_message)
    redis_conn.expire(redis_key, 30)
    
    return

AWS IoT Core와 Lambda를 연동하면, lambda_handler의 event 파라미터로 메시지의 JSON 데이터가 전송됩니다. 이 코드에서는 이 데이터에서 채널명을 파싱하여 ElastiCache(redis)에 저장할 키값으로 설정했고, 수신한 메시지(received_message) 전체를 30초의 TTL로 설정하여 저장했습니다. 다음으로 저장된 지난 대화 내용을 받아오는 GetLastMessage Lambda 함수의 코드를 살펴보겠습니다.

import json
import base64
import boto3
import redis
from datetime import datetime
from collections import OrderedDict

redis_conn = redis.StrictRedis(
    host='iotchatcache.xxx.ng.0001.apn2.cache.amazonaws.com', port=6379, db=0)

def lambda_handler(event, context):
    eventText = json.dumps(event)
  
    channel= event['pathParameters']['channel']
    match_key = channel + '*'

    return_data = {}
    
    for redis_key in redis_conn.scan_iter(match=match_key, count=1000):
        data = redis_conn.get(redis_key)
        
        key_str = redis_key.decode('utf-8')
        data_str = data.decode('utf-8')
     
        return_data[key_str] = data_str

    return_data = sorted(return_data.items())
    
    return {
        "statusCode": 200,
        "body": json.dumps(return_data)
    }

이 코드는 API Gateway를 통해 사용자가 채널에 접속할 때마다 호출되며, 해당 채널명을 키값으로 하는 메시지 전체의 내용을 ElastiCache(redis)에서 읽어와서 반환합니다. TTL 30초로 지정하여 저장했기 때문에 최근 30초간의 대화 기록이 반환될 것입니다.

이것으로 메시지를 주고받는 채팅의 기본적인 기능 외에 ‘지난 대화 보기’ 같은 추가 기능도 AWS 서비스와 연동하여 손쉽게 구현하였습니다. Lambda와 API Gateway 역시 서버리스 서비스로서 인프라 관리를 신경 쓰지 않아도, 필요한 만큼 리소스가 확장되어 부하 상황에서도 안정적으로 서비스 될 것입니다. ElastiCache도 오픈소스를 기반으로 하는 관리형 서비스입니다. 가장 범용적으로 쓰이는 오픈소스 인 메모리 데이터 스토어인 Redis (https://aws.amazon.com/ko/redis/) 와 Memcached (https://aws.amazon.com/ko/elasticache/memcached) 를 지원하며, AWS 콘솔이나 SDK를 통해 손쉽게 확장할 수 있습니다.


*4. 마치며*


게임 내의 필수 요소인 채팅 서비스를 AWS IoT Core를 사용하여 대규모 접속과 메시지 처리가 가능하도록 구현해봤습니다. ‘지난 대화 보기’ 기능도 AWS의 서버리스 서비스를 사용하여 유연한 구조로 구현했습니다. 게임은 게임성을 가르는 요소 외에도 수많은 기능과 시스템들이 복잡하게 구성돼있습니다. 이런 기능들을 독립적으로 분리하여 AWS 서비스를 활용하여 구성하면, 인프라 관리가 필요 없고 대규모 부하에 유연하며, 재사용이 가능한 서비스로 만들 수 있습니다.  마이크로서비스 아키텍처와 AWS를 적용해서 게임 개발 과정의 골칫거리들을 처리하고, 핵심 가치인 ‘재미’에 집중하시기 바랍니다!


