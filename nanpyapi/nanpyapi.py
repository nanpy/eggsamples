from flask import Flask
from arduino.arduino import arduino

app = Flask(__name__)
app.register_blueprint(arduino, url_prefix='/arduino')

if __name__ == '__main__':
    app.config['TRAP_BAD_REQUEST_ERRORS'] = True
    app.debug = True
    app.run()
