import os
import glob
import time
import subprocess

# These two lines mount the device:
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')
 
base_dir = '/sys/bus/w1/devices/'
# Get all the filenames begin with 28 in the path base_dir.
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'
def read_rom():
	name_file=device_folder+'/name'
	f = open(name_file,'r')
	return f.readline()

def speak(text):
    text = text.replace(" ", "_")  # Replace spaces with underscores to prevent parsing issues
    subprocess.run((
       "espeak \"" + text + "\" 2>/dev/null"
    ).split(" "))  # Construct the command and split into tokens for subprocess.run
 
def read_temp_raw():
	f = open(device_file, 'r')
	lines = f.readlines()
	f.close()
	return lines
 
def read_temp():
    lines = read_temp_raw()
    # Analyze if the last 3 characters are 'YES'.
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    # Find the index of 't=' in a string.
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        # Read the temperature .
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        temp_f = temp_c * 9.0 / 5.0 + 32.0
        return temp_f
 
print(' rom: '+ read_rom())

temperature = read_temp()
print(temperature)
rounded_temp = round(temperature)
time.sleep(1)
outputText = "The temperature in this room is currently " + str(rounded_temp) + " degrees Fahrenheit"
print(outputText)
speak(outputText)

