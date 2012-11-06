#!/usr/bin/env python

# Author: Andrea Stagi <stagi.andrea@gmail.com>
# Description: a clock synchronized with ntp server with an alarm controlled via Android
# Dependencies: nanpy, ntplib, bluetooth

from nanpy import (Servo, Lcd, Arduino, Tone)
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
        f = open(self.path, 'w')
        f.write("%d:%d:%d" % (h, m, on))
        f.close()

    def getAlarm(self):
        try:
            f = open(self.path, 'r')
            timestored = f.read()
            (h, m, on) = timestored.split(":")
            f.close()
            return (int(h), int(m), int(on))
        except IOError:
            self.setAlarm(0, 0, False)
            return (0, 0, False)

    def equal(self, time_str):
        (my_h, my_m) = time_str.split(":")
        (h, m, on) = self.getAlarm()
        if int(my_h) == h and int(my_m) == m:
            return True
        else:
            return False

ck = Clock()

class ClockThread (threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        while True:
            srv_sock = BluetoothSocket( RFCOMM )
            srv_sock.bind(("", 29))
            srv_sock.listen(400)
            port = srv_sock.getsockname()[1]
            advertise_service(srv_sock, "SynclockServer", 
            service_id = UUID,
            service_classes = [ UUID, 	SERIAL_PORT_CLASS ],
            profiles = [SERIAL_PORT_PROFILE])

            cli_sock, cli_info = srv_sock.accept()

            cli_sock.send("%d:%d:%d", ck.getAlarm())

            try:
                while True:
                    data = cli_sock.recv(3)
                    if len(data) == 0: break
                    ck.setAlarm(ord(data[0]),
                            ord(data[1]), 
			                ord(data[2]))
            except IOError:
                pass

            print "disconnected"

            cli_sock.close()
            srv_sock.close()
            print "all done"

            time.sleep(1)

class TimeThread (threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.play = False

    def run(self):
        global milltime
        while True:
            try:
                response = ntplib.NTPClient().request('europe.pool.ntp.org', version=3)
                milltime = int(response.tx_time)
                time_str = (datetime.fromtimestamp(milltime)).strftime('%H:%M')
                if ck.equal(time_str):
                    if not self.play:
                        PlayAlarmThread().start()
                        self.play = True
                else:
                    self.play = False
            except ntplib.NTPException:
                pass
            time.sleep(1)

class PlayAlarmThread (threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        tone = Tone(4)
        for i in range(5):
            tone.play(Tone.NOTE_C4, 250)
            time.sleep(0.1)

class TemperatureThread (threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        while True:
            temp = ((Arduino.analogRead(0) / 1024.0) * 5.0 - 0.5) * 100
            lcd.printString("- %0.1f\xDFC" % temp, 6, 1)
            time.sleep(60)

class ShowTimeThread (threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.c = 1
        self.servo = Servo(12)

    def run(self):
        global milltime
        while True:
            if milltime == 0:
                continue
            dt = datetime.fromtimestamp(milltime)
            lcd.printString(dt.strftime('%Y/%m/%d'), 0, 0)         
            lcd.printString(dt.strftime('%H:%M'), 0, 1)
            self.servo.write(90 + (30 * self.c))
            self.c *= -1
            time.sleep(1)

timeth = TimeThread()
timeth.start()
tempth = TemperatureThread()
tempth.start()
showth = ShowTimeThread()
showth.start()
clckth = ClockThread()
clckth.start()

raw_input('Press any key to stop...')

timeth._Thread__stop()
tempth._Thread__stop()
showth._Thread__stop()
clckth._Thread__stop()


