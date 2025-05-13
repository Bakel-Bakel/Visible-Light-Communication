import cv2
import numpy as np
import RPi.GPIO as GPIO
from time import sleep
from gpiozero import OutputDevice

GPIO.cleanup() 

# GPIO Setup
RELAY_PIN = 2
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(RELAY_PIN, GPIO.OUT)

# Set up relay control
relay = OutputDevice(RELAY_PIN, active_high=False, initial_value=True)  # Active LOW triggers relay

# Initialize USB Camera
camera = cv2.VideoCapture(0)  # Use the first connected camera

# Parameters for flashlight detection (e.g., threshold for brightness to detect flash)
brightness_threshold = 200  # Adjust based on your environment and camera sensitivity
blink_pattern = []  # Will store brightness values to detect blink pattern
time_window = 5  # seconds to store intensity for pattern detection
sample_rate = 0.2  # Seconds between samples (adjust this for faster/slower sampling)

# Time tracking variables
start_time = sleep_time = 0
previous_brightness = 0

# Function to detect flashlight blinking pattern
def detect_blink_pattern(brightness_values):
    """ Simple method to detect blink pattern based on light intensity. """
    # Simple pattern recognition based on brightness values. In real applications, more complex analysis can be done.
    average_brightness = np.mean(brightness_values)
    if average_brightness > brightness_threshold:
        return True  # Flash detected
    return False

# Main loop to capture video and detect flashlight blinking
try:
    while True:
        # Capture frame from the camera
        ret, frame = camera.read()
        if not ret:
            print("Failed to grab frame")
            break

        # Convert frame to grayscale (simplifies the analysis)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Compute the average brightness of the image
        brightness = np.mean(gray)

        # Track brightness changes to detect blinking
        blink_pattern.append(brightness)

        # Keep the pattern within the last 'time_window' seconds
        if len(blink_pattern) > time_window / sample_rate:
            blink_pattern.pop(0)

        # If a blink pattern is detected
        if detect_blink_pattern(blink_pattern):
            # Unlock solenoid (active low relay)
            relay.on()  # Unlock
            print("Solenoid is UNLOCKED")
        else:
            # Lock solenoid (active low relay)
            relay.off()  # Lock
            print("Solenoid is LOCKED")

        # Show the frame for debugging
        cv2.imshow("Camera Feed", frame)

        # Wait for a key press to stop (or use 'q' for quit)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        sleep(sample_rate)  # Adjust the sleep time for your sample rate

except KeyboardInterrupt:
    print("Program interrupted. Cleaning up...")

finally:
    # Clean up and release the camera
    GPIO.cleanup()
    camera.release()
    cv2.destroyAllWindows()
