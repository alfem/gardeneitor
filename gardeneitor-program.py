#!/usr/bin/python

import time
import signal
import sys
import ConfigParser

config = ConfigParser.SafeConfigParser()
config.read(("gardeneitor.ini","/etc/gardeneitor.ini"))
LOG_FILENAME=config.get("Main","log_filename")

# First relay starts the pump
PUMP=7
# These relays open/close the valves
RELAYS = (8, 11, 12, 15)
# END CONFIGURATION



def log(priority,text):
    with open(LOG_FILENAME,"a") as log:
      log.write(time.strftime("%Y/%m/%d %a %X ",time.localtime())+priority+": "+text+"\n")

def signal_handler(signal, frame):
        print('You pressed Ctrl+C!')
        GPIO.output(PUMP_PIN, 0)
        print " OFF "
        GPIO.cleanup()
        sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
        
try:
  import RPi.GPIO as GPIO
except RuntimeError:
  print("Error importing RPi.GPIO!  This is probably because you need superuser privileges.  You can achieve this by using 'sudo' to run your script")
    
    
  
def sprinkler(valve, min):
    print " valve pin", valve
    GPIO.setup(valve, GPIO.OUT)
    print " setup ok "
    print " opening valve"
    GPIO.output(valve, 1)
    print " valve open "
    print " watering for", min,'minutes'
    time.sleep(min*60)
    GPIO.output(valve, 0)
    print " valve closed "


# Use board pin sequential numbering 
GPIO.setmode(GPIO.BOARD)

GPIO.setup(PUMP, GPIO.OUT)
print "Starting pump"
GPIO.output(PUMP, 1)
log("I","Pump started (program)")
print "PUMP ON"
time.sleep(1)

try:
    with open(config.get("Main","program_data_filename"),'r') as f:
      for line in f:
          v,d=line.split(" ")
          relay=int(v)-1
          duration=int(d)
          log("I","Opening valve "+v+" for "+d+" minutes (program)")
          sprinkler(RELAYS[relay],duration)


except IOError:
    print "ERROR READING PROGRAM FILE:", config.get("Main","program_data_filename")
    log("E","ERROR READING PROGRAM FILE")

    pass      
except:
    print "ERROR IN PROGRAM FORMAT:", config.get("Main","program_data_filename")
    log("E","ERROR IN PROGRAM FORMAT")
    pass      
   

print "Stoping pump"
GPIO.output(PUMP, 0)
log("I","Pump stopped (program)")
print "PUMP OFF"
GPIO.cleanup()

