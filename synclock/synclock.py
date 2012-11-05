#!/usr/bin/env python

# Author: Andrea Stagi <stagi.andrea@gmail.com>
# Description: a clock synchronized with ntp server with an alarm controlled via Android
# Dependencies: nanpy, ntplib, bluetooth

from nanpy import (Servo, Lcd, Arduino)
from datetime import datetime
import ntplib, time, threading

lcd = Lcd([6, 7, 8, 9, 10, 11], [16, 2])
milltime = 0

class StopThread(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.stop = False

    def run(self):
        while not self.stop:
            self.elaborate()

    def stopMe(self):
        self.stop = True

    def elaborate(self):
        pass

class BluetoothThread (StopThread):

    def __init__(self):
        StopThread.__init__(self)

    def elaborate(self):
        time.sleep(1)

class TimeThread (StopThread):

    def __init__(self):
        StopThread.__init__(self)

    def elaborate(self):
        global milltime
        try:
            response = ntplib.NTPClient().request('europe.pool.ntp.org', version=3)
            milltime = int(response.tx_time)
        except ntplib.NTPException:
            pass
        time.sleep(1)

class TemperatureThread (StopThread):

    def __init__(self):
        StopThread.__init__(self)

    def elaborate(self):
        temp = ((Arduino.analogRead(0) / 1024.0) * 5.0 - 0.5) * 100
        lcd.printString("- %0.1f\xDFC" % temp, 6, 1)

        for i in range(60):
            if self.stop:
                return
            time.sleep(1)

class ShowTimeThread (StopThread):

    def __init__(self):
        StopThread.__init__(self)
        self.c = 1
        self.servo = Servo(12)

    def elaborate(self):
        global milltime
        if milltime == 0:
            return
        lcd.printString((datetime.fromtimestamp(milltime)).strftime('%Y-%m-%d'), 0, 0)
        lcd.printString((datetime.fromtimestamp(milltime)).strftime('%H:%M'), 0, 1)
        self.servo.write(90 + (30 * self.c))
        self.c *= -1
        Arduino.delay(1000)

timeth = TimeThread()
timeth.start()
tempth = TemperatureThread()
tempth.start()
showth = ShowTimeThread()
showth.start()
blueth = BluetoothThread()
blueth.start()

raw_input("Press any key to stop...")

timeth.stopMe()
tempth.stopMe()
showth.stopMe()
blueth.stopMe()


