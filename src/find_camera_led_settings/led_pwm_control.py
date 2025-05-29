#!/usr/bin/env python3
"""
Simple LED PWM Control Script
Controls an LED connected to GPIO12 using PWM.
"""

import RPi.GPIO as GPIO
import time

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
    print("LED PWM Control - Simple Version")
    print("Starting demo sequence...")

    print("Demo complete!")

    # Keep LED at 10% brightness
    pwm.ChangeDutyCycle(100)
    print("LED set to 10% brightness. Press Ctrl+C to exit.")

    # Keep running until interrupted
    while True:
        time.sleep(1)

except KeyboardInterrupt:
    print("\nExiting...")
    pwm.ChangeDutyCycle(0)  # Stop PWM
    GPIO.cleanup()  # Clean up GPIO

finally:
    # Clean up
    pwm.ChangeDutyCycle(0)
    GPIO.cleanup()
    print("GPIO cleaned up.")