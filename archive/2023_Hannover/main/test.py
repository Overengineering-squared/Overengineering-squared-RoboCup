import time

import cv2
import numpy as np
from picamera import PiCamera
from picamera.array import PiRGBArray

camera_x = 336
camera_y = 368
camera = PiCamera()
camera.resolution = (camera_x, camera_y)
rawCapture = PiRGBArray(camera, size=(camera_x, camera_y))
time.sleep(0.1)

average_left = np.array([[float(time.time()), float(0)]])  # saving the last turning values left
average_right = np.array([[float(time.time()), float(0)]])  # saving the last turning values right
start_time = time.time()
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    image = frame.array

    hsvImage = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    greenImage = cv2.inRange(hsvImage, (45, 100, 40), (75, 255, 255))
    # blacklineImage = cv2.inRange(image, (0, 0, 0), (90, 90, 90)) - greenImage

    kernal = np.ones((3, 3), np.uint8)  # removing noise
    greenImage = cv2.erode(greenImage, kernal, iterations=5)
    greenImage = cv2.dilate(greenImage, kernal, iterations=9)
    # blacklineImage = cv2.erode(blacklineImage, kernal, iterations=5)
    # blacklineImage = cv2.dilate(blacklineImage, kernal, iterations=9)

    green_contours, _ = cv2.findContours(greenImage, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

    position_black = [[]]
    lowest_green_sign = 0
    for i in range(len(green_contours)):
        black_detected = False
        if cv2.contourArea(green_contours[i]) > 1000:
            green_box = cv2.boxPoints(cv2.minAreaRect(green_contours[i]))

            roi = image[int(green_box[3][1]): int(green_box[3][1] + (camera_y * 0.2)), int(green_box[3][0]):int(green_box[2][0])]  # down
            if roi.size > 0:
                black = cv2.inRange(roi, (0, 0, 0), (75, 75, 75))
                if np.mean(black[:]) > 170:
                    if not black_detected:
                        position_black.append(["d"])
                        black_detected = True
                    else:
                        position_black[i + 1].append("d")

            roi = image[int(green_box[1][1]): int(green_box[2][1]), int(green_box[2][0]): int(green_box[2][0] + (camera_x * 0.2))]  # right
            if roi.size > 0:
                black = cv2.inRange(roi, (0, 0, 0), (75, 75, 75))
                if np.mean(black[:]) > 170:
                    if not black_detected:
                        position_black.append(["r"])
                        black_detected = True
                    else:
                        position_black[i + 1].append("r")

            roi = image[int(green_box[0][1]): int(green_box[3][1]), int(green_box[0][0] - (camera_x * 0.2)): int(green_box[0][0])]  # left
            if roi.size > 0:
                black = cv2.inRange(roi, (0, 0, 0), (75, 75, 75))
                if np.mean(black[:]) > 170:
                    if not black_detected:
                        position_black.append(["l"])
                        black_detected = True
                    else:
                        position_black[i + 1].append("l")

            roi = image[int(green_box[1][1] - (camera_y * 0.2)): int(green_box[1][1]), int(green_box[0][0]): int(green_box[1][0])]  # up
            if roi.size > 0:
                black = cv2.inRange(roi, (0, 0, 0), (75, 75, 75))
                if np.mean(black[:]) > 170:
                    if not black_detected:
                        position_black.append(["u"])
                        black_detected = True
                    else:
                        position_black[i + 1].append("u")

            if not black_detected:
                position_black.append(["n"])

            cv2.drawContours(image, [np.int0(green_box)], 0, (0, 255, 0), 3)
            # cv2.circle(image, (int(green_box[0][0]), int(green_box[0][1])), 8, (255, 255, 255), 2)
            # cv2.circle(image, (int(green_box[1][0]), int(green_box[1][1])), 8, (0, 255, 255), 2)
            # cv2.circle(image, (int(green_box[2][0]), int(green_box[2][1])), 8, (0, 0, 255), 2)

            # getting the position of the lowest corner of any greensign 
            green_box = green_box[green_box[:, 1].argsort()[::-1]]

            if green_box[0][1] > lowest_green_sign:
                lowest_green_sign = green_box[0][1]
        else:
            position_black.append(["n"])

    # getting the average turn direction
    if len(position_black) > 1:
        for i in range(len(position_black)):
            if "u" in position_black[i] and "l" in position_black[i]:  # turn right
                average_right = np.append(average_right, [[float(time.time() - start_time), float(1)]], axis=0)
                average_left = np.append(average_left, [[float(time.time() - start_time), float(0)]], axis=0)
            elif "u" in position_black[i] and "r" in position_black[i]:  # turn left
                average_left = np.append(average_left, [[float(time.time() - start_time), float(1)]], axis=0)
                average_right = np.append(average_right, [[float(time.time() - start_time), float(0)]], axis=0)
    else:
        average_right = np.append(average_right, [[float(time.time() - start_time), float(0)]], axis=0)
        average_left = np.append(average_left, [[float(time.time() - start_time), float(0)]], axis=0)

    average_right = average_right[np.where(average_right[:, 0] > ((time.time() - start_time) - 0.10))]
    average_left = average_left[np.where(average_left[:, 0] > ((time.time() - start_time) - 0.10))]

    # deciding how to turn
    right = False
    left = False
    straight = True
    turn_around = False

    if np.mean(average_right[:, 1]) > 0.5:
        right = True
        straight = False
    elif np.mean(average_left[:, 1]) > 0.5:
        left = True
        straight = False
    elif np.mean(average_right[:, 1]) > 0.3 and np.mean(average_left[:, 1]) > 0.3:
        right = False
        left = False
        straigt = False
        turn_around = True

    print("Left:")
    print(left)
    print("Right:")
    print(right)
    print("Straight:")
    print(straight)
    print("Turn around:")
    print(turn_around)

    cv2.imshow("Image", image)

    rawCapture.truncate(0)
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break

# # green
# if len(contours_grn) > 0:
#     for i in range(len(contours_grn)):
#         if cv2.contourArea(contours_grn[i]) > 1000:
#             x, y, w, h  = cv2.boundingRect(contours_grn[i]) # x,y,w,h (x,y top-left coordinate)
#             grn_roi = line_img[y:(y+h), int(x - camera_x * .2):x]
#             cv2.imshow("right", grn_roi)

#             grn_roi = line_img[y:(y+h), int(x - camera_x * .2):x]
#             cv2.imshow("right", grn_roi)

#             grn_roi = line_img[y:(y+h), int(x - camera_x * .2):x]
#             cv2.imshow("right", grn_roi)

#             grn_roi = line_img[y:(y+h), int(x - camera_x * .2):x]
#             cv2.imshow("right", grn_roi)


# cy = 0
# green_center = cv2.moments(contours_grn[i])
# if green_center['m00'] != 0:
#     #cx = int(green_center['m10']/green_center['m00'])
#     cy = int(green_center['m01']/green_center['m00'])
#     #cv2.circle(line_img, (cx, cy), 7, (0, 0, 255), -1)
