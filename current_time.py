import os
import glob
import time
import datetime
import subprocess

def speak(text):
    text = text.replace(" ", "_")  # Replace spaces with underscores to prevent parsing issues
    subprocess.run((
        "espeak \"" + text + "\" 2>/dev/null"
    ).split(" "))  # Construct the command and split into tokens for subprocess.run

now = datetime.datetime.now()

current_time = now.strftime("%I, %M %p")

speak("The current time is " + str(current_time))
