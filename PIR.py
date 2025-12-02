import RPi.GPIO as GPIO
import time
import subprocess

motionPin = 22

GPIO.setmode(GPIO.BOARD)
GPIO.setup(motionPin, GPIO.IN)
time.sleep(10)

try:
    while True:
        motion = GPIO.input(motionPin)
        if motion == 1:
            print("Motion detected!")
            subprocess.run(['espeak', '"Motion detected!"'])
        else:
            print("No motion detected.")
            subprocess.run(['espeak', '"No motion detected."'])
        time.sleep(0.5)
        break
except KeyboardInterrupt:
    GPIO.cleanup()
    print("GPIO Good to Go")

