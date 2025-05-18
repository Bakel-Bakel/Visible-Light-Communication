import cv2
import numpy as np
from gpiozero import OutputDevice, LED
from flask import Flask, render_template, request
from threading import Thread
from time import time, sleep

# === Hardware Setup ===
RELAY_PIN = 2
GREEN_LED_PIN = 17
RED_LED_PIN = 27

relay = OutputDevice(RELAY_PIN, active_high=False, initial_value=False)
green_led = LED(GREEN_LED_PIN)
red_led = LED(RED_LED_PIN)

relay.off()
green_led.off()
red_led.on()

# === Flash Detection Settings ===
flash_threshold = 200
min_flash_interval = 0.1
max_flash_duration = 1.5
flash_times = []

# === Control Flags ===
torch_mode_enabled = False

# === Flask App ===
app = Flask(__name__)
PASSWORD = "open123"  # Change this to your secure password

@app.route('/', methods=['GET', 'POST'])
def index():
    global torch_mode_enabled
    error = None
    if request.method == 'POST':
        entered_password = request.form.get('password')
        if entered_password == PASSWORD:
            torch_mode_enabled = True
        else:
            error = "Incorrect password!"
    return render_template('index.html', unlocked=torch_mode_enabled, error=error)

# === Camera & Torch Logic ===
def torch_monitor():
    global torch_mode_enabled
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Camera not accessible.")
        return

    try:
        while True:
            if not torch_mode_enabled:
                sleep(1)
                continue

            ret, frame = cap.read()
            if not ret:
                continue

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            brightness = np.mean(gray)
            current_time = time()

            if brightness > flash_threshold:
                if not flash_times or (current_time - flash_times[-1]) > min_flash_interval:
                    flash_times.append(current_time)
                    print(f"Flash at {current_time}, brightness={brightness}")

            # Remove old entries
            flash_times[:] = [t for t in flash_times if (current_time - t) <= max_flash_duration]

            if len(flash_times) >= 3:
                print("Flashes detected. Unlocking...")
                relay.on()
                green_led.on()
                red_led.off()

                sleep(6)

                relay.off()
                green_led.off()
                red_led.on()

                flash_times.clear()

    finally:
        cap.release()

# === Start Threads ===
if __name__ == '__main__':
    Thread(target=torch_monitor, daemon=True).start()
    app.run(host='0.0.0.0', port=5000)
