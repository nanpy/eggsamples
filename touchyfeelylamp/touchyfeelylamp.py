#!/usr/bin/env python

# Author: Andrea Stagi <stagi.andrea@gmail.com>
# Description:
# Dependencies: nanpy

from nanpy import (Arduino, CapacitiveSensor)

capSensor = CapacitiveSensor(4,2)
threshold = 1000
ledPin = 12;

Arduino.pinMode(ledPin, Arduino.OUTPUT)

while True:
    sensorValue = capSensor.capacitiveSensor(30)
     
    print(sensorValue)


    if sensorValue > threshold:
        Arduino.digitalWrite(ledPin, Arduino.HIGH)
    else:
        Arduino.digitalWrite(ledPin, Arduino.LOW)
       
    Arduino.delay(10)
