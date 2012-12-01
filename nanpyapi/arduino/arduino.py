from flask import Flask, Blueprint, Response, request, json
from nanpy import Arduino

arduino = Blueprint('arduino', __name__)

@arduino.route('/digitalpin/<int:pin_number>', methods=['GET', 'POST'])
def digitalpin(pin_number):
    if request.method == 'GET':
        Arduino.pinMode(pin_number, Arduino.INPUT)
        data = {
            'value' : Arduino.digitalRead(pin_number)
        }
        resp = Response(json.dumps(data), status=200, mimetype='application/json')
        return resp
    else:
        Arduino.pinMode(pin_number, Arduino.OUTPUT)
        Arduino.digitalWrite(pin_number, request.json['value'])
        resp = Response("", status=200, mimetype='application/json')
        return resp

@arduino.route('/analogpin/<int:pin_number>', methods=['GET', 'POST'])
def analogpin(pin_number):
    if request.method == 'GET':
        Arduino.pinMode(pin_number, Arduino.INPUT)
        data = {
            'value' : Arduino.analogRead(pin_number)
        }
        resp = Response(json.dumps(data), status=200, mimetype='application/json')
        return resp
    else:
        Arduino.pinMode(pin_number, Arduino.OUTPUT)
        Arduino.analogWrite(pin_number, request.json['value'])
        resp = Response("", status=200, mimetype='application/json')
        return resp

