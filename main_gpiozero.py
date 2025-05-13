import cv2
import numpy as np
from time import sleep
from gpiozero import OutputDevice
from flask import Flask, render_template, Response

# GPIO Setup
RELAY_PIN = 2
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

# Flask app setup
app = Flask(__name__)

# Function to detect flashlight blinking pattern
def detect_blink_pattern(brightness_values):
    """ Simple method to detect blink pattern based on light intensity. """
    average_brightness = np.mean(brightness_values)
    if average_brightness > brightness_threshold:
        return True  # Flash detected
    return False

# Generate frames for streaming to the browser
def generate_frames():
    while True:
        ret, frame = camera.read()
        if not ret:
            print("Failed to grab frame")
            break

        # Convert frame to grayscale
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
            relay.on()  # Unlock
            print("Solenoid is UNLOCKED")
            relay.close() 
        else:
            relay.off()  # Lock
            print("Solenoid is LOCKED")
            relay.close() 

        # Encode the frame in JPEG format for web streaming
        ret, jpeg = cv2.imencode('.jpg', frame)
        if not ret:
            continue
        frame = jpeg.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

# Route to display the video feed in the browser
@app.route('/')
def index():
    return render_template('index.html')  # This HTML file will display the video stream

# Route to stream the video feed
@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), 
                    mimetype='multipart/x-mixed-replace; boundary=frame')

# Run the Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
