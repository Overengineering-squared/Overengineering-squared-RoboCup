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
use_hsv = True

slider_max = 255
start_min = [0, 0, 0]
start_max = [30, 30, 30]

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


def remove_noise(image):
    kernal = np.ones((3, 3), np.uint8)  # removing noise
    image = cv2.erode(image, kernal, iterations=3)
    image = cv2.dilate(image, kernal, iterations=10)
    return image


cv2.namedWindow('slider')
cv2.createTrackbar('min_one', "slider", start_min[0], slider_max, nothing)
cv2.createTrackbar('min_two', "slider", start_min[1], slider_max, nothing)
cv2.createTrackbar('min_three', "slider", start_min[2], slider_max, nothing)

cv2.createTrackbar('max_one', "slider", start_max[0], slider_max, nothing)
cv2.createTrackbar('max_two', "slider", start_max[1], slider_max, nothing)
cv2.createTrackbar('max_three', "slider", start_max[2], slider_max, nothing)

while True:
    min_one = cv2.getTrackbarPos('min_one', 'slider')
    min_two = cv2.getTrackbarPos('min_two', 'slider')
    min_three = cv2.getTrackbarPos('min_three', 'slider')

    max_one = cv2.getTrackbarPos('max_one', 'slider')
    max_two = cv2.getTrackbarPos('max_two', 'slider')
    max_three = cv2.getTrackbarPos('max_three', 'slider')

    raw_capture = camera.capture_array()
    raw_capture = cv2.resize(raw_capture, (camera_x, camera_y))
    range_image = cv2.cvtColor(raw_capture, cv2.COLOR_RGBA2BGR)

    if use_hsv:
        range_image = cv2.cvtColor(raw_capture, cv2.COLOR_BGR2HSV)

    range_image = cv2.inRange(range_image, (min_one, min_two, min_three), (max_one, max_two, max_three))

    # uncomment to remove noise
    range_image = remove_noise(range_image)

    contours, hierarchy = cv2.findContours(range_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

    cv2.imshow("raw", raw_capture)
    cv2.imshow("range", range_image)

    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        print([min_one, min_two, min_three], [max_one, max_two, max_three])
        break
