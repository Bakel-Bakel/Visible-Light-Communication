import cv2
import numpy as np
from gpiozero import OutputDevice
from time import time, sleep

# GPIO Setup
RELAY_PIN = 2
relay = OutputDevice(RELAY_PIN, active_high=False, initial_value=False)  # Solenoid locked initially

# Camera setup
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise Exception("Camera not accessible")

# Flash detection parameters
flash_threshold = 200  # Adjust depending on environment
min_flash_interval = 0.1  # Minimum time between valid flashes (s)
max_flash_duration = 1.5  # Max total duration to allow 3 flashes (s)
flash_count = 0
flash_times = []

try:
    print("Monitoring for flashes...")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame.")
            continue

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        brightness = np.mean(gray)

        current_time = time()

        if brightness > flash_threshold:
            # Avoid double counting a single flash
            if not flash_times or (current_time - flash_times[-1]) > min_flash_interval:
                flash_times.append(current_time)
                print(f"Flash detected at {current_time}, brightness={brightness}")
        
        # Remove old flash times
        flash_times = [t for t in flash_times if (current_time - t) <= max_flash_duration]

        # If 3 flashes within window
        if len(flash_times) >= 3:
            print("3 flashes detected! Unlocking solenoid...")
            relay.on()
            sleep(6)  # Keep solenoid unlocked
            relay.off()
            print("Solenoid locked again.")

            flash_times.clear()  # Reset counter after activation

        # Optional: display for debugging
        # cv2.imshow('Frame', gray)
        # if cv2.waitKey(1) & 0xFF == ord('q'):
        #     break

except KeyboardInterrupt:
    print("Interrupted by user.")

finally:
    cap.release()
    cv2.destroyAllWindows()
    relay.off()
    print("Clean exit. Solenoid locked.")
