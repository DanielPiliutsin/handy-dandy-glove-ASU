#!/usr/bin/env python3
import RPi.GPIO as GPIO
import time
import subprocess
import os
import sys

# Button pin definitions
buttons = [26, 19, 13, 6]  # pinky, index, middle, pointer
thumb = 5
thumb_time = 0
thumb_pressed_flag = False
DELAY = 0.5

# Track button states
button_states = {}
last_action_time = 0

def run_script(script_name):
    """Runs a Python script and waits for it to complete."""
    try:
        # Get the directory of the current script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        script_path = os.path.join(script_dir, script_name)
        
        print(f"🔵 Attempting to run: {script_path}")
        
        # Check if file exists
        if not os.path.exists(script_path):
            print(f"❌ File not found: {script_path}")
            return False
        
        # Run the script and capture output
        result = subprocess.run(
            [sys.executable, script_path],
            cwd=script_dir,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        print(f"✅ Executed {script_name}")
        if result.stdout:
            print(f"Output: {result.stdout}")
        if result.stderr:
            print(f"Errors: {result.stderr}")
        
        return True
        
    except subprocess.TimeoutExpired:
        print(f"⏱️ {script_name} timed out after 30 seconds")
        return False
    except Exception as e:
        print(f"❌ Failed to run {script_name}: {type(e).__name__}: {e}")
        return False

def setup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    
    # Setup thumb button
    GPIO.setup(thumb, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    
    # Setup other buttons
    for pin in buttons:
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        button_states[pin] = False

def check_thumb():
    """Check if thumb button is currently pressed."""
    return GPIO.input(thumb) == GPIO.HIGH #LOW

def check_button(pin):
    """Check if a button is currently pressed."""
    return GPIO.input(pin) == GPIO.HIGH #LOW

def handle_button_press(pin):
    """Handle when a button is pressed."""
    global last_action_time
    
    # Debounce
    current_time = time.time()
    if current_time - last_action_time < 0.3:
        return
    
    last_action_time = current_time
    
    # Check if thumb is also pressed
    thumb_is_pressed = check_thumb()
    
    if thumb_is_pressed:
        print(f"🔘 Combo detected: Thumb + Button {pin}")
        run_thumb_combo(pin)
    else:
        print(f"🔘 Single button: {pin}")
        run_single(pin)

def run_single(channel):
    """Actions for single (non-thumb) button presses."""
    if channel == 6:
        print("Pointer only → Temperature")
        run_script("thermistor.py")
    elif channel == 13:
        print("Middle only → Time")
        run_script("current_time.py")
    elif channel == 19:
        print("Index only → Volume Up")
        run_script("Volume_Up.py")
    elif channel == 26:
        print("Pinky only → Volume Down")
        run_script("Volume_Down.py")

def run_thumb_combo(channel):
    """Actions for button + thumb combinations."""
    if channel == 6:
        print("Thumb + Pointer → Camera API")
        run_script("Camera_OpenAI.py")
    elif channel == 13:
        print("Thumb + Middle → Ultrasonic Front")
        run_script("ultrasonicfront.py")
    elif channel == 19:
        print("Thumb + Index → Ultrasonic Back")
        run_script("ultrasonicback.py")
    elif channel == 26:
        print("Thumb + Pinky → PIR Sensor")
        run_script("PIR.py")

def handle_thumb_only():
    """Handle thumb-only press."""
    global last_action_time
    
    current_time = time.time()
    if current_time - last_action_time < 0.3:
        return
    
    last_action_time = current_time
    print("🔘 Thumb only → Weather")
    run_script("weather.py")

def main_loop():
    """Main polling loop - checks button states continuously."""
    print("Button controller running. Press Ctrl+C to exit.")
    print(f"Script directory: {os.path.dirname(os.path.abspath(__file__))}")
    
    # Track previous states
    prev_thumb = False
    prev_buttons = {pin: False for pin in buttons}
    thumb_was_alone = False
    thumb_press_time = 0
    
    while True:
        try:
            # Check current states
            curr_thumb = check_thumb()
            curr_buttons = {pin: check_button(pin) for pin in buttons}
            
            # Detect thumb press
            if curr_thumb and not prev_thumb:
                thumb_press_time = time.time()
                thumb_was_alone = True
                print("👍 Thumb pressed")
            
            # Detect thumb release
            if not curr_thumb and prev_thumb:
                print("👍 Thumb released")
                # If thumb was pressed alone (no other buttons during press)
                if thumb_was_alone:
                    handle_thumb_only()
            
            # Check each button
            for pin in buttons:
                # Detect button press
                if curr_buttons[pin] and not prev_buttons[pin]:
                    # If thumb is currently pressed, it's not alone
                    if curr_thumb:
                        thumb_was_alone = False
                    handle_button_press(pin)
            
            # Update previous states
            prev_thumb = curr_thumb
            prev_buttons = curr_buttons.copy()
            
            time.sleep(0.01)  # 10ms polling rate
            
        except Exception as e:
            print(f"Error in main loop: {e}")
            time.sleep(0.1)

def destroy():
    """Cleanup GPIO on exit."""
    print("\n🛑 Cleaning up GPIO...")
    GPIO.cleanup()
    print("✅ GPIO cleaned up")

if __name__ == '__main__':
    try:
        setup()
        main_loop()
    except KeyboardInterrupt:
        print("\n⚠️ Keyboard interrupt received")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
    finally:
        destroy()
