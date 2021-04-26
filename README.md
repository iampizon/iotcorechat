
# 게임 채팅 서버 AWS IoT Core 로 한방에 구현하기 

## Blog
https://aws.amazon.com/ko/blogs/korea/implementing-game-chat-application-with-aws-iot-core/

이 저장소는 위 블로그에서 다룬 아키텍처의 실제 구현과 소스들을 제공합니다. 


## Architecutre
![아키텍처 이미지](https://github.com/iampizon/iotcorechat/blob/master/iotcorechat-architecture.png "AWS IoT Core Chat Service")


## Lambda
/lambda/message_watcher.py
- IoT Core의 채팅 메시지를 구독하여 동작하는 람다 펑션입니다. 차단당한 사용자의 메시지나 악성 단어가 포함된 메시지를 필터링하고, 지난 메시지 보기 기능을 위해 30초의 TTL을 걸어 Redis 에 메시지를 기록해둡니다.  

/lambda/get_channel_last_message.py
- Redis에 기록된 지난 메시지를 불러옵니다. 최초 채널에 접속했을 때 호출됩니다.

/lambda/get_user_info.py
- 차단당한 유저의 정보를 DDB에 기록합니다.

/lambda/layer_aws_xray_sdk.zip, /lambda/layer_redis.zip
- 각 람다 펑션에서 사용하는 레이어(공통모듈)들입니다. 람다의 내부 프로세스를 트레이스하기위한 Xray SDK와 Redis에 접속하기위한 SDK가 포함되있습니다.

## Test Client(python)
/test-client/iotcorechat-testclient.py


![테스트 클라이언트 이미지](https://github.com/iampizon/iotcorechat/blob/master/test-client/screentshot.png "AWS IoT Core Chat Client")


python의 UI라이브러리인 QT5( https://www.qt.io/qt-for-python ) 로 구현된 
테스트 클라이언트 
테스트 클라이언트 입니다.


## Test Bot(python)
/test-bot/iotcorechat_testbot.py

/test-bot/run_chat_100.sh

/test-bot/run_chat_100_repeater.sh
