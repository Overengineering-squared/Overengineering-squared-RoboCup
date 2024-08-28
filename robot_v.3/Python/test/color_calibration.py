import os
import time

import cv2
import numpy as np
from libcamera import controls
from picamera2 import Picamera2

# Disable libcamera and Picamera2 logging
Picamera2.set_logging(Picamera2.ERROR)
os.environ["LIBCAMERA_LOG_LEVELS"] = "4"

camera_num = 1
use_hsv = False

slider_max = 255
start_min = [0, 0, 0]
start_max = [75, 75, 75]

if camera_num == 1:
    camera_x = 448
    camera_y = 252

    camera = Picamera2()

    mode = camera.sensor_modes[0]
    camera.configure(camera.create_video_configuration(sensor={'output_size': mode['size'], 'bit_depth': mode['bit_depth']}))

    camera.start()
    camera.set_controls({"AfMode": controls.AfModeEnum.Manual, "LensPosition": 6.5, "FrameDurationLimits": (1000000 // 50, 1000000 // 50)})  # {"AfMode": controls.AfModeEnum.Manual, "LensPosition": 0.4} {"AfMode": controls.AfModeEnum.Continuous, "AfSpeed": controls.AfSpeedEnum.Fast}
    time.sleep(0.1)

elif camera_num == 2:
    camera_x = 640
    camera_y = 480

    camera = Picamera2(1)
    camera.start()


def nothing(x):
    pass


def find_average_color(image):
    avg_color_per_row = np.average(image, axis=0)
    avg_color = np.average(avg_color_per_row, axis=0)
    return avg_color


square_size = 15

while True:
    raw_capture = camera.capture_array()
    raw_capture = cv2.resize(raw_capture, (camera_x, camera_y))
    raw_capture = cv2.cvtColor(raw_capture, cv2.COLOR_RGBA2BGR)

    if use_hsv:
        calibaration_image = cv2.cvtColor(raw_capture, cv2.COLOR_BGR2HSV)
    else:
        calibaration_image = raw_capture

    cv2.rectangle(raw_capture, (camera_x // 2 - square_size, (camera_y // 2 + 30) - square_size), (camera_x // 2 + square_size, (camera_y // 2 + 30) + square_size), (0, 0, 255), 2)
    cv2.imshow("raw", raw_capture)

    key = cv2.waitKey(1) & 0xFF
    if key == ord("w"):
        average_color = find_average_color(calibaration_image[(camera_y // 2 + 30) - square_size:(camera_y // 2 + 30) + square_size, camera_x // 2 - square_size:camera_x // 2 + square_size])
        average_color_min = np.array([average_color[0] - 25, average_color[1] - 60, average_color[2] - 40])
        average_color_max = np.array([average_color[0] + 25, average_color[1] + 60, average_color[2] + 70])

        print(np.clip(np.rint(average_color_min), 0, 255), np.clip(np.rint(average_color_max), 0, 255))
    if key == ord("q"):
        break
