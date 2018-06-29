#!/usr/bin/python

import time
import signal
import sys

# CONFIGURATION
DATA_PATH="/tmp"
PROGRAM_FILE=DATA_PATH+"/gardeneitor.dat"
CRONTAB_USER='alfem'

# First relay starts the pump
PUMP=7
# These relays open/close the valves
VALVES = (8, 11, 12, 15)
# END CONFIGURATION


def signal_handler(signal, frame):
        print('You pressed Ctrl+C!')
        GPIO.output(VALVE_PIN, 0)
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
print " starting pump"
GPIO.output(PUMP, 1)
print " PUMP ON "
time.sleep(1)

sprinkler(8,1)
time.sleep(10)
sprinkler(11,1)
time.sleep(10)
sprinkler(12,15)

print " stoping pump"
GPIO.output(PUMP, 0)
GPIO.cleanup()

