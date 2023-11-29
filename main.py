import ssl
from ultralytics import YOLO

import cv2
import numpy as np
import math
import time
# import serial

# import for blynk
import BlynkLib

BLYNK_AUTH = 'gvoIwiZ41DCdq0_rW2LE68oWw8yYR5Ks'
# initialize Blynk
blynk = BlynkLib.Blynk(BLYNK_AUTH)
# blynk = BlynkLib.Blynk(BLYNK_AUTH, server="blynk-cloud.com", port=9443)
# blynk = BlynkLib.Blynk(BLYNK_AUTH, server="sgp1.blynk.cloud", port=9443)

# initialize time
tmr_start_time = time.time()

# Initialize Arduino serial communication
# arduino = serial.Serial('COM7', 9600)
# time.sleep(2)  # Allow time for Arduino to establish connection

# Load yoloV8 trained model
model = YOLO('catfish30.pt')
# Load class labeled "gasping_catfish"
classNames = ["gasping_catfish"]

# Replace "ESP32_CAMERA_URL" with the URL of the ESP32 camera video stream
# stream_url = "http://192.168.1.140:81/stream?source=sensor"
# stream_url = "http://192.168.4.1:81/stream?source=sensor" # local host
# stream_url = "http://192.168.1.140:81/stream?source=sensor" # via internet
# stream_url = "http://192.168.1.140:81/stream" # via web server
# stream_url = "http://192.168.1.140/mjpeg/1" # via multiple client
stream_url = "https://9379-49-150-45-78.ngrok-free.app/mjpeg/1"

# Load video stream
cap = cv2.VideoCapture(stream_url)
# cap = cv2.VideoCapture(0)

# Initialize gasping catfish total
gasping_catfish_estimation = 0

# Initialize catfish total
catfish_total = 1

# Initialize alert level
alert_level = ""

# initialize value of aerator_status
aerator_status = 0

# aerator interval operation
aerator_operation = 0

# Run-time Duration of operation
duration = 5400

# Duration of interval per operation
duration_stop = 0
# global duration, duration_stop
# FUNCTIONS FOR BLYNK
# .......................................................................................................................................................



@blynk.on("connected") # First to execute
def blynk_connected():
    # You can also use blynk.sync_virtual(pin)
    # to sync a specific virtual pin
    # Updating V1,V2,V3 values from the server
    blynk.sync_virtual(1,2,3)

@blynk.on("V1") # Third to execute
def v1_write_handler(value):
    global aerator_status
    aerator_status = int(value[0])

@blynk.on("V2")
def v2_write_handler(value):
    global aerator_operation
    aerator_operation = int(value[0])  # Convert the received value to an integer

@blynk.on("V3") # Second to execute
def v3_write_handler(value):
    global catfish_total
    catfish_total = value[0]

# def interval_func():
#     global duration, duration_stop
#     if aerator_operation == 0: # Automatic Mode
#         # print(aerator_operation)
#         # Automatic control
#         if gasping_catfish_estimation > 30:
#             # Send command to Arduino to activate the relay and start aerator
#             blynk.virtual_write(1, 1)
#             # arduino.write(b'1')
#         elif gasping_catfish_estimation == 0:
#             # Send command to Arduino to stop the aerator
#             blynk.virtual_write(1, 0)
#             # arduino.write(b'0')
#
#     elif aerator_operation == 1: # 3 Hours mode
#         # arduino.write(b'1')
#         blynk.virtual_write(1, 1)
#         time.sleep(duration)
#         # Down-time duration
#         duration_stop = 10800
#         # arduino.write(b'0')
#         blynk.virtual_write(1, 0)
#         time.sleep(duration_stop)
#
#     elif aerator_operation == 2: # 6 Hours mode
#         # arduino.write(b'1')
#         blynk.virtual_write(1, 1)
#         time.sleep(duration)
#         # Down-time duration
#         duration_stop = 21600
#         # arduino.write(b'0')
#         blynk.virtual_write(1, 0)
#         time.sleep(duration_stop)
#
#     elif aerator_operation == 3: # 8 Hours mode
#         # arduino.write(b'1')
#         blynk.virtual_write(1, 1)
#         time.sleep(duration)
#         # Down-time duration
#         duration_stop = 28800
#         # arduino.write(b'0')
#         blynk.virtual_write(1, 0)
#         time.sleep(duration_stop)
#
#     elif aerator_operation == 4: # Manual mode
#         # Turn on aerator
#         if aerator_status == 0:
#             # blynk.virtual_write(1, 0)
#             pass
#             # arduino.write(b'0')
#         # Turn off aerator
#         elif aerator_status == 1:
#             # blynk.virtual_write(1, 1)
#             pass
#             # arduino.write(b'1')

while True:
    ret, frame = cap.read()

    results = model(frame, stream=True, conf=0.25)

    gasping_catfish_count = 0

    for r in results:
        boxes = r.boxes
        gasping_catfish_count += len(boxes)

        for box in boxes:
            x1, y1, x2, y2 = box.xyxy[0]
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 3)

            confidence = math.ceil((box.conf[0] * 100)) / 100
            print("Confidence: ", confidence)

            cls = int(box.cls[0])
            print("Class Name: ", classNames[cls])

            org = [x1, y1]
            cv2.putText(frame, classNames[cls], [x1, y1], cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 1)

        # cv2.putText(frame, f"Gasping Catfish Count: {gasping_catfish_count}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        # cv2.imshow('ONLYFINS', frame)

    gasping_catfish_estimation = (gasping_catfish_count / float(catfish_total)) * 100
    if (gasping_catfish_estimation - int(gasping_catfish_estimation) >= 0.5):
        # Round up to the nearest integer and convert to int
        gasping_catfish_estimation = int(math.ceil(gasping_catfish_estimation))
    else:
        gasping_catfish_estimation = int(math.floor(gasping_catfish_estimation))

    # Alert levels
    if gasping_catfish_estimation == 0:
        alert_level = "No Alert"
    elif gasping_catfish_estimation in range(1, 10):
        alert_level = "Low Alert (Level 1)"
    elif gasping_catfish_estimation in range(10, 31):
        alert_level = "Moderate Alert (Level 2)"
    elif gasping_catfish_estimation in range(31, 51):
        alert_level = "High Alert (Level 3)"
    else:
        alert_level = "Critical Alert (Level 4)"

    # Display the resulting frame with catfish count
    # cv2.putText(frame, f"Catfish Total: {catfish_total}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
    # cv2.putText(frame, f"Catfish Gasping: {gasping_catfish_estimation}% - {alert_level}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

    # Aerator interval operation
    # interval_func()
    print(aerator_operation)
    if aerator_operation == 0:  # Automatic Mode

        # Automatic control
        if gasping_catfish_estimation > 30:
            # Send command to Arduino to activate the relay and start aerator
            blynk.virtual_write(1, 1)
            # arduino.write(b'1')
        elif gasping_catfish_estimation == 0:
            # Send command to Arduino to stop the aerator
            blynk.virtual_write(1, 0)
            # arduino.write(b'0')

    elif aerator_operation == 1:  # 3 Hours mode
        # arduino.write(b'1')
        blynk.virtual_write(1, 1)
        time.sleep(duration)
        # Down-time duration
        duration_stop = 10800
        # arduino.write(b'0')
        blynk.virtual_write(1, 0)
        time.sleep(duration_stop)

    elif aerator_operation == 2:  # 6 Hours mode
        # arduino.write(b'1')
        blynk.virtual_write(1, 1)
        time.sleep(duration)
        # Down-time duration
        duration_stop = 21600
        # arduino.write(b'0')
        blynk.virtual_write(1, 0)
        time.sleep(duration_stop)

    elif aerator_operation == 3:  # 8 Hours mode
        # arduino.write(b'1')
        blynk.virtual_write(1, 1)
        time.sleep(duration)
        # Down-time duration
        duration_stop = 28800
        # arduino.write(b'0')
        blynk.virtual_write(1, 0)
        time.sleep(duration_stop)

    elif aerator_operation == 4:  # Manual mode
        # Turn on aerator
        if aerator_status == 0:
            # blynk.virtual_write(1, 0)
            pass
            # continue
            # arduino.write(b'0')
        # Turn off aerator
        elif aerator_status == 1:
            # blynk.virtual_write(1, 1)
            pass
            # continue
            # arduino.write(b'1')

    # cv2.imshow('OnlyFins', frame)

    # Break the loop on 'q' key press
    # if cv2.waitKey(1) & 0xFF == ord('q'):
    #     break

    # ------------------------------------------------------------------------------------------------------------------------------------------------------ #
    # START OF BLYNK PROCESS
    blynk.run()

    t = time.time()
    # sends data after every 1 second
    if t - tmr_start_time > 1:
        blynk.virtual_write(4, gasping_catfish_estimation)
        blynk.virtual_write(5, alert_level)
        tmr_start_time += 1

# Release resources
# cap.release()
# cv2.destroyAllWindows()
