#!/bin/bash
number=1
while [ $number -le $1 ]
do
echo "staring... ${number}"
nohup ./run_chat_100.sh &
number=$(($number+1))
sleep 10 
done

