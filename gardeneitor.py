#!/usr/bin/python

# GARDENEITOR
# Raspberry Pi Garden Valves Automation and Web Interface
# by Alfonso E.M. <alfonso@el-magnifico.org>

# Requieres Flash, gpio, and python-crontab
# (sudo pip install flash flask_bootstrap python-crontab)


from __future__ import print_function

import sys

from flask import Flask
from flask import make_response
from flask import render_template
from flask import request
from flask_bootstrap import Bootstrap
from crontab import CronTab

# CONFIGURATION
CRONTAB_USER='alfem'
APP_PATH="/home/"+CRONTAB_USER+"/gardeneitor"
PROGRAM_DATA_FILENAME=APP_PATH+"/gardeneitor.dat"
PROGRAM_BIN_FILENAME=APP_PATH+"/gardeneitor-program.py"

# First relay starts the pump
PUMP=7
# These relays open/close the valves
VALVES = (8, 11, 12, 15)
# END CONFIGURATION


cron = CronTab(user=CRONTAB_USER)  

try:
    import RPi.GPIO as GPIO
except:
    GPIO=False


error_msg = '{msg:"error"}'
success_msg = '{msg:"success"}'



# SETUP GPIO
def init_relays():

    if GPIO:
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)
        GPIO.setup(PUMP, GPIO.OUT)
        for v in VALVES:
            GPIO.setup(v, GPIO.OUT)

def reset_gpio():
  GPIO.cleanup()

# CHECK GPIO STATE
def check_relays():

    status=[] 
    if GPIO:
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)
        GPIO.setup(PUMP, GPIO.IN)
        for v in VALVES:
            GPIO.setup(v, GPIO.IN)
            status.append(GPIO.input(v))
    else:
        status=[False]*len(VALVES)


# SWITCH ON/OFF PUMP
def switch_pump(state):

    print ("Switching pump ->"+str(state))
    if GPIO:
        GPIO.setup(PUMP, GPIO.OUT)
        GPIO.output(PUMP,state) 


# SWITCH ON/OFF A VALVE
def switch_valve(v,state):
    print ("Switching valve "+str(v)+"->"+str(state))
    if GPIO:
        GPIO.setup(v, GPIO.OUT)
        GPIO.output(v,state) 


# Setup web app
app = Flask(__name__)
bootstrap = Bootstrap(app)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/program-save', methods=('get', 'post'))
def program_save():
    scheduleTime = request.form.get('scheduleTime')
    program = request.form.get('program')
    print ("Saving program")

    try:
        hh,mm=scheduleTime.split(':')
    except:
        return make_response("", 404)
        

    jobs = cron.find_comment('gardeneitor')     
    try:
        job=jobs.next()
        job.clear()
    except StopIteration:
        job = cron.new(command=PROGRAM_BIN_FILENAME, comment="gardeneitor")  
        
    job.hour.on(hh)
    job.minute.on(mm)
    for dow in ('MON','TUE','WED','THU','FRI','SAT','SUN'): 
        if request.form.get(dow): 
            job.dow.also.on(dow)        
    cron.write()

    with open(PROGRAM_DATA_FILENAME,'w') as f:
        f.write(program)

    return make_response("0", 200)


@app.route('/pump/<int:state>')
def api_pump(state):
    switch_pump(True)
    if state:
        print("PUMP ON")
        return make_response("1", 200)
    else:
        print("PUMP OFF")
        return make_response("0", 200)

@app.route('/valve/<int:valve>/<int:state>')
def api_valve(valve,state):
    switch_valve(valve,state)
    if state:
        print("VALVE ON")
        return make_response("1", 200)
    else:
        print("VALVE OFF")
        return make_response("0", 200)


@app.route('/status/')
def api_get_status():
    res = relay_get_port_status(relay)
    if res:
        print("Relay is ON")
        return make_response("1", 200)
    else:
        print("Relay is OFF")
        return make_response("0", 200)


@app.route('/log/')
def api_get_log():
    if res:
        print("Relay is ON")
        return make_response("1", 200)
    else:
        print("Relay is OFF")
        return make_response("0", 200)


@app.route('/stop-all/')
def api_stop_all(relay):
    print("STOP-ALL")
    switch_pump(False)
    for v in VALVES:
        switch_valve(v,False)
    return make_response(success_msg, 200)


@app.errorhandler(404)
def page_not_found(e):
    print("ERROR: 404")
    return render_template('404.html', the_error=e), 404


@app.errorhandler(500)
def internal_server_error(e):
    print("ERROR: 500")
    return render_template('500.html', the_error=e), 500


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)

