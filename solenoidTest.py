import RPi.GPIO as GPIO
from time import sleep

# Define the GPIO pin connected to the relay IN pin
RELAY_PIN = 17

# Setup
GPIO.setmode(GPIO.BCM)          # Use BCM pin numbering
GPIO.setup(RELAY_PIN, GPIO.OUT) # Set pin as output

# Turn on the relay (solenoid ON)
GPIO.output(RELAY_PIN, GPIO.LOW)  # Active LOW triggers relay
print("Solenoid is ON - Unlocked")
sleep(5)  # Keep it ON for 5 seconds

# Turn off the relay (solenoid OFF)
GPIO.output(RELAY_PIN, GPIO.HIGH)
print("Solenoid is OFF - Locked")

# Cleanup
GPIO.cleanup()

