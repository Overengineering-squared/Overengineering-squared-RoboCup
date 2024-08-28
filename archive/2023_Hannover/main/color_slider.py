import time

import cv2
import numpy as np
from picamera import PiCamera
from picamera.array import PiRGBArray

camera_x = 336
camera_y = 280
camera = PiCamera()
camera.resolution = (camera_x, camera_y)
rawCapture = PiRGBArray(camera, size=(camera_x, camera_y))
time.sleep(0.1)

black_min_one = 0
black_min_two = 0
black_min_three = 0

black_max_one = 10
black_max_two = 10
black_max_three = 10

slider_max = 255


def nothing(x):
    pass


cv2.namedWindow('image')
cv2.createTrackbar('black_min_one', "image", 225, slider_max, nothing)
cv2.createTrackbar('black_min_two', "image", 225, slider_max, nothing)
cv2.createTrackbar('black_min_three', "image", 225, slider_max, nothing)

cv2.createTrackbar('black_max_one', "image", 255, slider_max, nothing)
cv2.createTrackbar('black_max_two', "image", 255, slider_max, nothing)
cv2.createTrackbar('black_max_three', "image", 255, slider_max, nothing)

for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    line_img = frame.array
    # line_img = cv2.cvtColor(line_img, cv2.COLOR_BGR2HSV)

    blacklineImage = cv2.inRange(line_img, (black_min_one, black_min_two, black_min_three), (black_max_one, black_max_two, black_max_three))

    kernal = np.ones((3, 3), np.uint8)  # removing noise
    blacklineImage = cv2.erode(blacklineImage, kernal, iterations=3)
    blacklineImage = cv2.dilate(blacklineImage, kernal, iterations=10)

    contours_blk, hierarchy_blk = cv2.findContours(blacklineImage, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    if len(contours_blk) > 0:
        for blackline in contours_blk:
            # if cv2.contourArea(blackline) > 2000:
            line_img = cv2.drawContours(line_img, blackline, -1, (255, 255, 255), 3)
            # print(cv2.contourArea(blackline))

    black_min_one = cv2.getTrackbarPos('black_min_one', 'image')
    black_min_two = cv2.getTrackbarPos('black_min_two', 'image')
    black_min_three = cv2.getTrackbarPos('black_min_three', 'image')

    black_max_one = cv2.getTrackbarPos('black_max_one', 'image')
    black_max_two = cv2.getTrackbarPos('black_max_two', 'image')
    black_max_three = cv2.getTrackbarPos('black_max_three', 'image')

    cv2.imshow("img", line_img)
    cv2.imshow("bla", blacklineImage)
    cv2.imshow("image", np.zeros([200, 400, 3], dtype=np.uint8))

    rawCapture.truncate(0)
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break
