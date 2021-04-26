
# 게임 채팅 서버 AWS IoT Core 로 한방에 구현하기 

## Blog
https://aws.amazon.com/ko/blogs/korea/implementing-game-chat-application-with-aws-iot-core/

이 저장소는 위 블로그에서 다룬 아키텍처의 실제 구현과 소스들을 제공합니다. 


## Architecutre
![아키텍처 이미지](https://github.com/iampizon/iotcorechat/blob/master/iotcorechat-architecture.png "AWS IoT Core Chat Service")


## Lambda
/lambda/message_watcher.py

/lambda/get_channel_last_message.py

/lambda/get_user_info.py

/lambda/layer_aws_xray_sdk.zip
/lambda/layer_redis.zip

## Test Client(python)
/test-client/iotcorechat-testclient.py
![테스트 클라이언트 이미지](https://github.com/iampizon/iotcorechat/blob/master/test-client/screentshot.png "AWS IoT Core Chat Client")


## Test Bot(python)
/test-bot/iotcorechat_testbot.py

/test-bot/run_chat_100.sh

/test-bot/run_chat_100_repeater.sh
