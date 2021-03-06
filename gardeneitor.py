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
from flask import jsonify
from flask_bootstrap import Bootstrap
from crontab import CronTab
import ConfigParser
import time
config = ConfigParser.SafeConfigParser()
config.read(("gardeneitor.ini","/etc/gardeneitor.ini"))
LOG_FILENAME=config.get("Main","log_filename")
import psutil

# First relay starts the pump
PUMP=7
# These relays open/close the valves
RELAYS = (8, 11, 12, 15)
# END CONFIGURATION



cron = CronTab(user=config.get("Main","crontab_user"))  

try:
    import RPi.GPIO as GPIO
except:
    GPIO=False


error_msg = '{msg:"error"}'
success_msg = '{msg:"success"}'


def log(priority,text):
    with open(LOG_FILENAME,"a") as log:
      log.write(time.strftime("%Y/%m/%d %a %X ",time.localtime())+priority+": "+text+"\n")

# SETUP GPIO
def init_relays():

    if GPIO:
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)
        GPIO.setup(PUMP, GPIO.OUT)
        for r in RELAYS:
            GPIO.setup(r, GPIO.OUT)
        log("I","Relays initialized")

def reset_gpio():
  GPIO.cleanup()

# CHECK GPIO STATE
def check_status():

    status=[] 
    if GPIO:
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)
        GPIO.setup(PUMP, GPIO.IN)
        status.append(GPIO.input(PUMP))
        for r in RELAYS:
            GPIO.setup(r, GPIO.IN)
            status.append(GPIO.input(r))
    else:
        status=[False]*len(RELAY)

    return status

# SWITCH ON/OFF PUMP
def switch_pump(state):

    print ("Switching pump ->"+str(state))
    if GPIO:
        init_relays()
        GPIO.output(PUMP,state) 
        if state == 0: 

          log("I","Pump stopped")
        else: 
          log("I","Pump started")


# SWITCH ON/OFF A VALVE
def switch_valve(v,state):
    print ("Switching valve "+str(v)+"->"+str(state))
    if GPIO:
        init_relays()
        r=RELAYS[v-1] 
        GPIO.output(r,state) 
        log("I","Valve "+str(v)+" changed to "+str(state))


class ReverseProxied(object):
    '''Wrap the application in this middleware and configure the 
    front-end server to add these headers, to let you quietly bind 
    this to a URL other than / and to an HTTP scheme that is 
    different than what is used locally.

    In nginx:
    location /myprefix {
        proxy_pass http://192.168.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Scheme $scheme;
        proxy_set_header X-Script-Name /myprefix;
        }

    :param app: the WSGI application
    '''
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        script_name = environ.get('HTTP_X_SCRIPT_NAME', '')
        if script_name:
            environ['SCRIPT_NAME'] = script_name
            path_info = environ['PATH_INFO']
            if path_info.startswith(script_name):
                environ['PATH_INFO'] = path_info[len(script_name):]

        scheme = environ.get('HTTP_X_SCHEME', '')
        if scheme:
            environ['wsgi.url_scheme'] = scheme
        return self.app(environ, start_response)

# Setup web app
app = Flask(__name__)
app.wsgi_app = ReverseProxied(app.wsgi_app)
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
        job = cron.new(command=config.get("Main","program_bin_filename"), comment="gardeneitor")  
        
    job.hour.on(hh)
    job.minute.on(mm)
    for dow in ('MON','TUE','WED','THU','FRI','SAT','SUN'): 
        if request.form.get(dow): 
            job.dow.also.on(dow)        
    cron.write()

    with open(config.get("Main","program_data_filename"),'w') as f:
        f.write(program)

    return make_response("0", 200)


@app.route('/program-read', methods=('get', 'post'))
def program_read():
    print ("Reading program")

    jobs = cron.find_comment('gardeneitor')     
    try:
        job=jobs.next()
    except StopIteration:
        return make_response("")
        
    hour=str(job.hour)
    minute=str(job.minute)
    dow=str(job.dow)        

    print ("Crontab:"+hour+":"+minute+"->"+dow)

    with open(config.get("Main","program_data_filename"),'r') as f:
        program=f.read()

    return jsonify({'hour': hour, 'minute': minute, 'dow': dow, 'program':program})


@app.route('/program-switch/<int:state>')
def api_program_switch(state):
    jobs = cron.find_comment('gardeneitor')     
    try:
        job=jobs.next()
        if state:
          job.enable()
        else: 
          job.enable(False)
        cron.write()
    except StopIteration:
        return make_response("1", 200)  

    return make_response("0", 200)  

@app.route('/program-run')
def api_program_run():
    jobs = cron.find_comment('gardeneitor')     
    try:
        job=jobs.next()
        job.run()
        cron.write()
    except StopIteration:
        return make_response("1", 200)  

    return make_response("0", 200)  

@app.route('/program-state')
def api_program_state():
    jobs = cron.find_comment('gardeneitor')     
    return make_response("1", 200)  

    return make_response("0", 200)  

@app.route('/program-run-state')
def api_program_run_state():

# I do not know why psutil shortens the program name
    if ("gardeneitor-pro" in (p.name() for p in psutil.process_iter()) ):
      return make_response("1", 200)  
    else:
      return make_response("0", 200)  


@app.route('/pump/<int:state>')
def api_pump(state):
    switch_pump(state)
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
    status = check_status()
    print (status) 
    return jsonify(status=status)

@app.route('/log')
def api_get_log():
   with open(LOG_FILENAME,"r") as log:
#      loglines=log.read()
      loglines=tail(log,10)     
      print (loglines)
      return make_response(loglines)


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



# Tail file function: https://stackoverflow.com/questions/136168/get-last-n-lines-of-a-file-with-python-similar-to-tail
def tail( f, lines=20 ):
    total_lines_wanted = lines

    BLOCK_SIZE = 1024
    f.seek(0, 2)
    block_end_byte = f.tell()
    lines_to_go = total_lines_wanted
    block_number = -1
    blocks = [] # blocks of size BLOCK_SIZE, in reverse order starting
                # from the end of the file
    while lines_to_go > 0 and block_end_byte > 0:
        if (block_end_byte - BLOCK_SIZE > 0):
            # read the last block we haven't yet read
            f.seek(block_number*BLOCK_SIZE, 2)
            blocks.append(f.read(BLOCK_SIZE))
        else:
            # file too small, start from begining
            f.seek(0,0)
            # only read what was not read
            blocks.append(f.read(block_end_byte))
        lines_found = blocks[-1].count('\n')
        lines_to_go -= lines_found
        block_end_byte -= BLOCK_SIZE
        block_number -= 1
    all_read_text = ''.join(reversed(blocks))
    return '\n'.join(all_read_text.splitlines()[-total_lines_wanted:])



if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)

