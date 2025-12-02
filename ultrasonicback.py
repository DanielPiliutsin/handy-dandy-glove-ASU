#!/usr/bin/env python3

import RPi.GPIO as GPIO
import time
import subprocess

# Define GPIO pins
TRIG = 18      # GPIO pin connected to Trig of Ultrasonic Sensor
ECHO = 16      # GPIO pin connected to Echo of Ultrasonic Sensor


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

def speak(text):
    text = text.replace(" ", "_")  # Replace spaces with underscores to prevent parsing issues
    subprocess.run((
        "espeak \"" + text + "\" 2>/dev/null"
    ).split(" "))  # Construct the command and split into tokens for subprocess.run

def speakDis():
    dis = distance()
    print(f"Back: Distance is {dis:.2f} centimeters")
    speak_message = f"Distance is {dis:.2f} centimeters"
    speak(speak_message)
       

def loop():
    """ Main loop that checks the distance and controls the buzzer """
    while True:
        dis = distance()
        print(round(dis, 2), 'cm')
        time.sleep(0.3)

def explode():
    """ Cleanup function to reset GPIO settings """
    print('BOOOM!')
    GPIO.cleanup()

if __name__ == "__main__":
    setup()
    try:
        speakDis()
    except KeyboardInterrupt:
        explode()
