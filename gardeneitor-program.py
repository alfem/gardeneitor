#!/usr/bin/python

import time
import signal
import sys


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
    
    
# Use board pin sequential numbering 
GPIO.setmode(GPIO.BOARD)


# Pin 11 is GPIO17    
PUMP_PIN=7
#RELAY PINS 7,8,11,12,15,16,21,22
    
def sprinkler(valve, min):

    GPIO.setmode(GPIO.BOARD)
    print "Valve pin", valve
    GPIO.setup(PUMP_PIN, GPIO.OUT)
    GPIO.setup(valve, GPIO.OUT)
    print " setup ok "

    print " starting pump"
    GPIO.output(PUMP_PIN, 1)
    print " PUMP ON "
    time.sleep(1)
    print " opening valve"
    GPIO.output(valve, 1)
    print " VALVE OPEN "
    time.sleep(min*60)


    GPIO.output(valve, 0)
    GPIO.output(PUMP_PIN, 0)
    print " OFF "
    GPIO.cleanup()


sprinkler(8,1)
time.sleep(10)
sprinkler(11,1)
time.sleep(10)
sprinkler(12,15)

