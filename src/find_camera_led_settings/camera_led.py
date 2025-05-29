import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
import board
import neopixel_spi as neopixel
from data_processing.utils.camera_class import Pizero_Camera
import RPi.GPIO as GPIO
import time



camera=Pizero_Camera()
camera.start()  # Start the camera to ensure it is ready  # Set resolution to 640x480
camera.set_exposure(10000)  # Set exposure time to 10000us (10ms)
DELAY = 2  


# Configuration
LED_PIN = 12
PWM_FREQUENCY = 1000 

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN, GPIO.OUT)

# Create PWM instance
pwm = GPIO.PWM(LED_PIN, PWM_FREQUENCY)
pwm.start(0)  # Start with 0% duty cycle (LED off)

try:
    

    pwm.ChangeDutyCycle(100)
    time.sleep(DELAY)  # Delay to allow the color to be visible
    camera.save_image("test.jpg")
    frame= camera.capture_image(format="jpeg")  # Capture image and save to file
    with open("captured_frame.jpeg", "wb") as f:
        f.write(frame)

    # Keep the script running until interrupted
    while True:
        time.sleep(1)
        
except KeyboardInterrupt:
    print("\nExiting...")
    pwm.stop()  # Stop PWM
    #pwm.ChangeDutyCycle(0)  # Stop PWM
    GPIO.cleanup()  # Clean up GPIO
    
finally:
    print("\nExiting...")
    #pwm.ChangeDutyCycle(0)
    pwm.stop()  # Stop PWM
    GPIO.cleanup()  # Clean up GPIO
