import RPi.GPIO as GPIO
import time

class PwmLed:
    """
    A class to control a single LED using PWM for brightness control.
    
    Args:
        pin (int): The GPIO pin number the LED is connected to (BCM numbering).
        frequency (int, optional): PWM frequency in Hz. Defaults to 1000.
    """
    
    def __init__(self, pin=12, frequency=1000):
        """Initialize the LED with the specified pin and frequency."""
        self.pin = pin
        self.frequency = frequency
        self.pwm = None
        self.is_setup = False
        
    def setup(self):
        """Set up the GPIO pin and PWM for the LED."""
        if not self.is_setup:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.pin, GPIO.OUT)
            self.pwm = GPIO.PWM(self.pin, self.frequency)
            self.pwm.start(0)  # Start with LED off
            self.is_setup = True
    
    def set_brightness(self, brightness):
        """
        Set the brightness of the LED.
        
        Args:
            brightness (float): Brightness level from 0 to 100.
        """
        if not self.is_setup:
            self.setup()
        
        # Ensure brightness is within valid range
        brightness = max(0, min(100, brightness))
        self.pwm.ChangeDutyCycle(brightness)
    
    def on(self):
        """Turn the LED on at full brightness."""
        self.set_brightness(100)
    
    def off(self):
        """Turn the LED off."""
        self.set_brightness(0)
    
    def cleanup(self):
        """Clean up resources used by the LED."""
        if self.is_setup and self.pwm is not None:
            self.pwm.stop()
            self.is_setup = False

