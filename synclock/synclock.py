#!/usr/bin/env python

# Author: Andrea Stagi <stagi.andrea@gmail.com>
# Description: a clock synchronized with ntp server with an alarm controlled via Android
# Dependencies: nanpy, ntplib, bluetooth

from nanpy import (Servo, Lcd, Arduino)
from datetime import datetime
import ntplib, time, threading

from bluetooth import *

UUID = "00001101-0000-1000-8000-00805F9B34FB"

lcd = Lcd([6, 7, 8, 9, 10, 11], [16, 2])
milltime = 0

class Clock():
    
    def __init__(self, path = 'synclockalarm'):
        self.path = path
        self.getAlarm()

    def setAlarm(self, h, m, on=True):
        self.h = h
        self.m = m
        self.on = on
        f = open(self.path, 'w')
        f.write("%d:%d:%d" % (h, m, on))
        f.close()

    def getAlarm(self):
        try:
            f = open(self.path, 'r')
            timestored = f.read()
            (self.h, self.m, self.on) = timestored.split(":")
            f.close()
        except IOError:
            self.setAlarm(0, 0, False)
        return (self.h, self.m, self.on)

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

class ClockThread (StopThread):

    def __init__(self):
        StopThread.__init__(self)
        self.ck = Clock()

    def elaborate(self):
        #waiting for connection
        server_sock=BluetoothSocket( RFCOMM )
        server_sock.bind(("", 29))
        server_sock.listen(400)

        port = server_sock.getsockname()[1]


        advertise_service( server_sock, "SampleServer",
                           service_id = UUID,
                           service_classes = [ UUID, SERIAL_PORT_CLASS ],
                           profiles = [ SERIAL_PORT_PROFILE ] )

        print "Waiting for connection on RFCOMM channel %d" % port

        client_sock, client_info = server_sock.accept()
        print "Accepted connection from ", client_info

        #send h m and on to device
        print self.ck.getAlarm()

        #listen device
        #get h, m and on

        try:
            while not self.stop:
                data = client_sock.recv(3)
                if len(data) == 0: break
                self.ck.setAlarm(data[0], data[1], data[2])
        except IOError:
            pass

        print "disconnected"

        client_sock.close()
        server_sock.close()
        print "all done"

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
clckth = ClockThread()
clckth.start()

raw_input('Press any key to stop...')

timeth.stopMe()
tempth.stopMe()
showth.stopMe()
clckth.stopMe()


