from gpiozero import OutputDevice
from time import sleep

# Define the GPIO pin connected to the relay IN pin
RELAY_PIN = 2

# Setup for Active High Relay (active_high=True)
relay = OutputDevice(RELAY_PIN, active_high=True, initial_value=False)  # Active HIGH triggers relay

# Turn on the relay (solenoid ON)
relay.on()  # Relay ON (solenoid unlocked)
print("Solenoid is ON - Unlocked")
sleep(5)  # Keep it ON for 5 seconds

# Turn off the relay (solenoid OFF)
relay.off()  # Relay OFF (solenoid locked)
print("Solenoid is OFF - Locked")
