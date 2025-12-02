import ultrasonicfront as uf
import ultrasonicback as ub

def speak(text):
    text = text.replace(" ", "_")
    subprocess.run((
        "espeak \"" + text + "\" 2>/dev/null"
    ).split(" "))
    
def loop():
    while True:
       speak(f"Distance is {dis:.2f} centimeters")

def destroy():
    GPIO.cleanup()

if __name__ == "__main__":
    setup()
    try:
        loop()
    except KeyboardInterrupt:
        destroy()
