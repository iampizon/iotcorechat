#!/bin/bash
number=1
while [ $number -le 100 ]
do
nohup py ./iot_chat_testbot.py &
number=$(($number+1))
sleep 1
done

