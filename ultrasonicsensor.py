#!/usr/bin/env python3

import RPi.GPIO as GPIO
import time

# Define GPIO pins
TRIG = 11      # GPIO pin connected to Trig of Ultrasonic Sensor
ECHO = 12      # GPIO pin connected to Echo of Ultrasonic Sensor


def setup():
    """ Setup the GPIO pins for the ultrasonic sensor and buzzer """
    GPIO.setmode(GPIO.BOARD)
    
    # Setup for ultrasonic sensor
    GPIO.setup(TRIG, GPIO.OUT)
    GPIO.setup(ECHO, GPIO.IN)
    
  

def distance():
    """ Measure the distance using the ultrasonic sensor """
    GPIO.output(TRIG, 0)
    time.sleep(0.000002)
    GPIO.output(TRIG, 1)
    time.sleep(0.00001)
    GPIO.output(TRIG, 0)

    while GPIO.input(ECHO) == 0:
        pass
    time1 = time.time()
    
    while GPIO.input(ECHO) == 1:
        pass
    time2 = time.time()

    duration = time2 - time1
    return (duration * 340 / 2)




def loop():
    """ Main loop that checks the distance and controls the buzzer """
    while True:
        dis = distance()
        print(round(dis, 2), 'cm')  # Print distance measurement
        time.sleep(0.3)

def explode():
    """ Cleanup function to reset GPIO settings """
    print('BOOOM!')
    GPIO.cleanup()

if __name__ == "__main__":
    setup()
    try:
        loop()
    except KeyboardInterrupt:
        explode()
