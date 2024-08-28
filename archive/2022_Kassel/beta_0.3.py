import time

import cv2
# import sensor_serial as se
import motor
import numpy as np
from picamera import PiCamera
from picamera.array import PiRGBArray

# camera resolution 
camera_x = 368
camera_y = 208

# camera Setup
camera = PiCamera()
camera.resolution = (camera_x, camera_y)
camera.rotation = 180  # camera is mounted upside down
rawCapture = PiRGBArray(camera, size=(camera_x, camera_y))

time.sleep(0.1)

# fps counter
fps_time = time.time()
counter = 0
fps = 0

x_last = camera_x / 2  # saving the x value of the last line center

for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    image = frame.array  # Creating a variable with the contents of the frame
    hsvImage = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)  # Converting the BGR image to a HSV image

    blacklineImage = cv2.inRange(image, (0, 0, 0), (85, 85, 85))  # definig colour for the line
    # cv2.circle(blacklineImage, (int(camera_x/2), camera_y), int(camera_x/2  + 260/2), (0, 255, 0), 255) # drawing a black circle on the binary line image
    cv2.ellipse(blacklineImage, (int(camera_x / 2), camera_y), (int(camera_x / 2 + 255 / 2), int(camera_y + 255 / 2)), 0, 0, 360, (0, 0, 0), 255)

    kernal = np.ones((3, 3), np.uint8)  # removing noise
    blacklineImage = cv2.erode(blacklineImage, kernal, iterations=5)
    blacklineImage = cv2.dilate(blacklineImage, kernal, iterations=9)

    contours_blk, hierarchy_blk = cv2.findContours(blacklineImage, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)  # getting every black contour in the image
    if len(contours_blk) > 0:

        # getting the correct contour to follow
        candidates = np.array([[0, 0, 0, 0, 0, camera_x]])
        off_bottom = 0

        for con_num in range(len(contours_blk)):
            box = cv2.boxPoints(cv2.minAreaRect(contours_blk[con_num]))  # get the corners of a box around the contour
            box = box[box[:, 1].argsort()[::-1]]  # sort them by their y values and reverse
            candidates = np.append(candidates, [[con_num, int(box[0][0] + 0.5), int(box[0][1] + 0.5), int(box[1][0] + 0.5), int(box[1][1] + 0.5), camera_x]], axis=0)  # append the x and y values of the bottom corners to the candidates array

            if box[0][1] >= (camera_y * 0.95):  # if a contour is at the bottom of the screen
                off_bottom = off_bottom + 1

        candidates = candidates[candidates[:, 2].argsort()[::-1]]  # sort candidates by their y values of the lowes corner and reverse

        if off_bottom > 1:
            for con_num in range(len(candidates[:(off_bottom)])):
                (con_num, x_cor1, y_cor1, x_cor2, y_cor2, x_distance) = candidates[con_num]
                candidates[con_num] = (con_num, x_cor1, y_cor1, x_cor2, y_cor2, abs(x_last - ((x_cor1 + x_cor2) / 2)))  # add the distance between the last x and current

            candidates = candidates[candidates[:, 5].argsort()]  # sort candidates by their x_distance

        blackline = contours_blk[candidates[0][0]]

        box = cv2.boxPoints(cv2.minAreaRect(blackline))  # get the corners of blackbox
        box = box[box[:, 1].argsort()[::-1]]  # sort by y values and reverse
        x_last = (box[0][0] + box[1][0]) / 2  # save new x_last value

        blacklineSorted = blackline[blackline[:, :, 1].argsort()[::-1]]  # sorting the contour points by their y values
        poi = blacklineSorted[0][0][0][0], blacklineSorted[0][0][0][1]  # store the highest point
        ang = int((poi[0] - camera_x / 2) / (camera_x / 2) * 180)  # calculate to angle to turn
        motor.steer(ang)

        # visualations 
        image = cv2.circle(image, (poi), 5, (0, 0, 255), -1)
        image = cv2.putText(image, str(ang), (0, int(camera_y * 0.12)), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
        image = cv2.drawContours(image, blackline, -1, (200, 50, 150), 3)

    # fps counter 
    counter += 1
    if (time.time() - fps_time) > 1:
        fps = int(counter / (time.time() - fps_time))
        counter = 0
        fps_time = time.time()
    cv2.putText(image, str(fps), (int(camera_x * 0.92), int(camera_y * 0.1)), cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 0, 255), 1)

    cv2.imshow("image", image)  # show the bgr picture
    cv2.imshow("hsvImage", hsvImage)  # show the bgr picture
    cv2.imshow("blacklineImage", blacklineImage)  # show the blackline picture

    rawCapture.truncate(0)
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break
