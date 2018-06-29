#!/usr/bin/python

import time
import signal
import sys

# CONFIGURATION
CRONTAB_USER='alfem'
APP_PATH="/home/"+CRONTAB_USER+"/gardeneitor"
PROGRAM_DATA_FILENAME=APP_PATH+"/gardeneitor.dat"
PROGRAM_BIN_FILENAME=APP_PATH+"/gardeneitor-program.py"

# First relay starts the pump
PUMP=7
# These relays open/close the valves
RELAYS = (8, 11, 12, 15)
# END CONFIGURATION


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
print "PUMP ON"
time.sleep(1)

try:
    with open(PROGRAM_DATA_FILENAME,'r') as f:
      for line in f:
          valve,duration=line.split(" ")
          relay=int(valve)-1
          sprinkler(RELAYS[relay],int(duration))
except IOError:
    print "ERROR READING PROGRAM FILE:", PROGRAM_DATA_FILENAME
    pass      
except:
    print "ERROR IN PROGRAM FORMAT:", PROGRAM_DATA_FILENAME
    pass      
   

print "Stoping pump"
GPIO.output(PUMP, 0)
print "PUMP OFF"
GPIO.cleanup()

