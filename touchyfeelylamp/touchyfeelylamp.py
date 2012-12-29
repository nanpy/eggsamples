#!/usr/bin/env python

# Author: Andrea Stagi <stagi.andrea@gmail.com>
# Description: a lamp that turns a light on and off when you touch a piece of conductive material
# Dependencies: nanpy > 6.0

from nanpy import (Arduino, CapacitiveSensor)

capSensor = CapacitiveSensor(4,2)
threshold = 1000
ledPin = 12;

Arduino.pinMode(ledPin, Arduino.OUTPUT)

while True:
    sensorValue = capSensor.capacitiveSensor(30)
     
    print("Capacitive sensor value: %d" % sensorValue)

    if sensorValue > threshold:
        Arduino.digitalWrite(ledPin, Arduino.HIGH)
    else:
        Arduino.digitalWrite(ledPin, Arduino.LOW)
       
    Arduino.delay(10)
