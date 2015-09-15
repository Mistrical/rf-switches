#!/usr/bin/python
from flask import Flask
from flask.ext.restless import APIManager
from flask.ext.sqlalchemy import SQLAlchemy

import time
import pigpio
import lwrfCustom

# Constants
TX_REPEAT = 2

# Globals
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///switches.db'
db = SQLAlchemy(app)
pi = pigpio.pi() # Connect to local Pi.
tx = lwrfCustom.tx(pi, 25) # Specify Pi, tx gpio, and baud.


class Switch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    type = db.Column(db.Text)
    room = db.Column(db.Text)
    on_command = db.Column(db.Text)
    off_command = db.Column(db.Text)

db.create_all()

api_manager = APIManager(app, flask_sqlalchemy_db=db)
api_manager.create_api(Switch, methods=['GET', 'POST', 'DELETE', 'PUT'])


@app.route('/api/switch/<int:id>/<int:command>')
def command_rf(id, command):
    s = Switch.query.filter_by(id=id).first()
    
    if command == 1:
        print "Turning on switch", s.name.encode('ascii','ignore'),  "with command ", s.on_command.encode('ascii','ignore')
        tx.put(s.on_command.encode('ascii','ignore'), TX_REPEAT)
    elif command == 0:
        print "Turning off switch",s.name.encode('ascii','ignore'), "with command ", s.off_command.encode('ascii','ignore')
        tx.put(s.off_command.encode('ascii','ignore'), TX_REPEAT)
    
    return 'OK'


@app.route('/')
def index():
        return app.send_static_file("index.html")

if __name__ == "__main__":
    app.debug = True
    app.run(host='0.0.0.0')
