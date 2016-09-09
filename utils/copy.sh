#!/bin/bash 
COUNTER=0
while true; do
	oiltemp=$(cat /sys/bus/w1/devices/28-02155377b2ff/w1_slave | grep  -E -o ".{0,0}t=.{0,6}" | cut -c 3-)
	#oiltemp=$(cat /home/sysop/test | grep  -E -o ".{0,0}t=.{0,6}" | cut -c 3-)
	#echo $oiltemp
	#if [ $oiltemp -gt 90000 ]; then
	if [[ $oiltemp == *"="* ]]; then
		#echo "="
		#smalloiltemp=$(cat /home/sysop/test | grep  -E -o ".{0,0}t=.{0,6}" | cut -c 3-)
		smalloiltemp=$(cat /sys/bus/w1/devices/28-02155377b2ff/w1_slave | grep  -E -o ".{0,0}t=.{0,5}" | cut -c 3-)
		echo $smalloiltemp>/home/sysop/sensoroil
	else
		#echo "kein ="
		echo $oiltemp>/home/sysop/sensoroil
	fi
	#fi
	watertemp=$(cat /sys/bus/w1/devices/28-02155370a7ff/w1_slave | grep  -E -o ".{0,0}t=.{0,5}" | cut -c 3-)
	echo $watertemp>/home/sysop/sensorwater
	sleep .5 
done


