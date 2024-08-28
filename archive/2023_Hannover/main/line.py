import math
import multiprocessing
import time

import cv2
import numpy as np
from picamera import PiCamera
from picamera.array import PiRGBArray

manager = multiprocessing.Manager()
line_angle = manager.Value("i", 0)
line_count = manager.Value("i", 1)
status = manager.Value("c", "line")
turn_dir = manager.Value("i", "straight")
terminate = manager.Value("i", False)


def line_loop(black_min=(0, 0, 0), black_max=(85, 85, 85), green_min=(40, 50, 20), green_max=(80, 255, 255), red_min_1=(0, 100, 90), red_max_1=(10, 255, 255), red_min_2=(170, 100, 100), red_max_2=(180, 255, 255)):
    camera_x = 336
    camera_y = 368
    camera = PiCamera()
    camera.resolution = (camera_x, camera_y)
    rawCapture = PiRGBArray(camera, size=(camera_x, camera_y))
    time.sleep(0.1)

    # fps counter
    fps_time = time.perf_counter()
    counter = 0
    fps = 0

    x_last = camera_x / 2
    for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
        line_img_name = "line"
        cv2.namedWindow(line_img_name)
        cv2.moveWindow(line_img_name, 342, 86)

        line_img = frame.array

        hsvImage = cv2.cvtColor(line_img, cv2.COLOR_BGR2HSV)
        greenImage = cv2.inRange(hsvImage, green_min, green_max)
        redImage = cv2.inRange(hsvImage, red_min_1, red_max_1) + cv2.inRange(hsvImage, red_min_2, red_max_2)
        blacklineImage = cv2.inRange(line_img, black_min, black_max) - greenImage

        kernal = np.ones((3, 3), np.uint8)  # removing noise
        greenImage = cv2.erode(greenImage, kernal, iterations=5)
        greenImage = cv2.dilate(greenImage, kernal, iterations=9)
        redImage = cv2.erode(redImage, kernal, iterations=5)
        redImage = cv2.dilate(redImage, kernal, iterations=9)
        blacklineImage = cv2.erode(blacklineImage, kernal, iterations=9)
        blacklineImage = cv2.dilate(blacklineImage, kernal, iterations=9)

        if status.value == "ramp_up" or status.value == "ramp_down":
            cv2.rectangle(blacklineImage, (0, 0), (camera_x, int(camera_y * .5)), (0), -1)
        elif status.value == "obstacle":
            cv2.rectangle(blacklineImage, (0, 0), (camera_x, int(camera_y * .25)), (0), -1)

        contours_blk, hierarchy_blk = cv2.findContours(blacklineImage, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)  # getting every black contour in the image
        contours_grn, hierarchy_grn = cv2.findContours(greenImage, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)  # get every green sign in the image
        contours_red, hierarchy_grn = cv2.findContours(redImage, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)  # get every green sign in the image

        for i in range(len(contours_red)):
            if cv2.contourArea(contours_red[i]) > 15000:
                status.value = "stop"

        line_count.value = len(contours_blk)
        if len(contours_blk) > 0:

            # getting the correct contour to follow
            candidates = np.array([[0, 0, 0, 0, 0, camera_x]])
            off_bottom = 0

            for con_num in range(len(contours_blk)):
                box = cv2.boxPoints(cv2.minAreaRect(contours_blk[con_num]))  # get the corners of a box around the contour
                box = box[box[:, 1].argsort()[::-1]]  # sort them by their y values and reverse
                candidates = np.append(candidates, [[con_num, int(box[0][0]), int(box[0][1]), int(box[1][0]), int(box[1][1]), camera_x]], axis=0)  # append the x and y values of the bottom corner to the candidates array

                if box[0][1] >= (camera_y * 0.95):  # if a contour is at the bottom of the screen
                    off_bottom += 1

            candidates = candidates[candidates[:, 2].argsort()[::-1]]  # sort candidates by their y values of the lowes corner and reverse

            if off_bottom > 1:
                for con_num in range(len(candidates[:(off_bottom)])):
                    (con_num, x_cor1, y_cor1, x_cor2, y_cor2, x_distance) = candidates[con_num]
                    candidates[con_num] = (con_num, x_cor1, y_cor1, x_cor2, y_cor2, abs(x_last - ((x_cor1 + x_cor2) / 2)))  # add the distance between the last x and current

                candidates = candidates[candidates[:, 5].argsort()]  # sort candidates by their x_distance

            x_last = (candidates[0][1] + candidates[0][3]) / 2
            blackline = contours_blk[candidates[0][0]]

            # calculate angle
            blackline_y_min = np.amin(blackline[:, :, 1])
            blackline_top = blackline[np.where(blackline[:, 0, 1] == blackline_y_min)]
            top_mean = (int(np.mean(blackline_top[:, :, 0])), blackline_y_min)
            poi = np.array([[0, top_mean[0], top_mean[1]]])

            blackline_x_min = np.amin(blackline[:, :, 0])
            blackline_left = blackline[np.where(blackline[:, 0, 0] == blackline_x_min)]
            # blackline_left = blackline_left[blackline_left[:,0,1].argsort()[::-1]]
            # left_mean = blackline_left[0][0]
            left_mean = (blackline_x_min, int(np.mean(blackline_left[:, :, 1])))
            poi = np.append(poi, [[0, left_mean[0], left_mean[1]]], axis=0)

            blackline_x_max = np.amax(blackline[:, :, 0])
            blackline_right = blackline[np.where(blackline[:, 0, 0] == blackline_x_max)]
            # blackline_right = blackline_right[blackline_right[:,0,1].argsort()[::-1]]
            # right_mean = blackline_right[0][0]
            right_mean = (blackline_x_max, int(np.mean(blackline_right[:, :, 1])))
            poi = np.append(poi, [[0, right_mean[0], right_mean[1]]], axis=0)

            center = (camera_x / 2, camera_y)
            black_top = False
            for i in range(len(poi)):
                (distance, poi_x, poi_y) = poi[i]
                if i == 0 and poi_y < camera_y * .1:
                    black_top = True

                distance = abs(math.sqrt(math.pow(center[0] - poi_x, 2) + math.pow(center[1] - poi_y, 2)))
                if (i == 1 and poi_x < camera_x * 0.1 and not black_top) or (i == 2 and poi_x > camera_x * 0.9 and not black_top) or poi_y < camera_y * 0.05:
                    distance = distance + camera_y * 2

                if i == 1 and turn_dir.value == "left":
                    distance = distance + camera_y * 5
                elif i == 2 and turn_dir.value == "right":
                    distance = distance + camera_y * 5

                poi[i] = (distance, poi_x, poi_y)
                # print(poi)

            poi = poi[poi[:, 0].argsort()[::-1]]
            line_angle.value = int((poi[0][1] - camera_x / 2) / (camera_x / 2) * 180)  # calculate to angle to turn

            # green turn signs
            if len(contours_grn) > 0:
                green_black_detected = np.zeros((len(contours_grn), 4), dtype=np.int8)  # green signs [b,t,l,r], [b,t,l,r]
                for i in range(len(contours_grn)):
                    if cv2.contourArea(contours_grn[i]) > 5000:
                        green_box = cv2.boxPoints(cv2.minAreaRect(contours_grn[i]))

                        green_box = green_box[green_box[:, 1].argsort()]
                        # bottom
                        roi_b = blacklineImage[int(green_box[3][1]):min(int(green_box[3][1] + (camera_y * 0.2)), camera_y), min(int(green_box[2][0]), int(green_box[3][0])):max(int(green_box[2][0]), int(green_box[3][0]))]
                        if roi_b.size > 0:
                            if np.mean(roi_b[:]) > 150:
                                green_black_detected[i, 0] = 1

                        # top
                        roi_t = blacklineImage[max(int(green_box[0][1] - (camera_y * 0.2)), 0):int(green_box[0][1]), min(int(green_box[0][0]), int(green_box[1][0])):max(int(green_box[0][0]), int(green_box[1][0]))]
                        if roi_t.size > 0:
                            if np.mean(roi_t[:]) > 150:
                                green_black_detected[i, 1] = 1

                        green_box = green_box[green_box[:, 0].argsort()]
                        # left
                        roi_l = blacklineImage[min(int(green_box[0][1]), int(green_box[1][1])):max(int(green_box[0][1]), int(green_box[1][1])), max(int(green_box[0][0] - (camera_x * 0.2)), 0):int(green_box[0][0])]
                        if roi_l.size > 0:
                            if np.mean(roi_l[:]) > 150:
                                green_black_detected[i, 2] = 1

                        # right
                        roi_r = blacklineImage[min(int(green_box[2][1]), int(green_box[3][1])):max(int(green_box[2][1]), int(green_box[3][1])), int(green_box[3][0]):min(int(green_box[3][0] + (camera_x * 0.2)), camera_x)]
                        if roi_r.size > 0:
                            if np.mean(roi_r[:]) > 150:
                                green_black_detected[i, 3] = 1
                else:
                    turn_dir.value = "straight"

                turn_left = False
                turn_right = False
                for i in green_black_detected:
                    if np.sum(i) == 2:
                        if i[1] == 1 and i[2] == 1:
                            turn_right = True
                        elif i[1] == 1 and i[3] == 1:
                            turn_left = True

                if turn_left and not turn_right:
                    turn_dir.value = "left"
                elif turn_right and not turn_left:
                    turn_dir.value = "right"
                elif turn_left and turn_right:
                    turn_dir.value = "turn_around"
                elif not turn_left and not turn_right:
                    turn_dir.value = "straight"
                # line_img = cv2.putText(line_img, str(green_black_detected), (0, int(camera_y * 0.5)), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

            # visuals
            for black in contours_blk:
                line_img = cv2.drawContours(line_img, black, -1, (0, 0, 255), 3)
            for green in contours_grn:
                line_img = cv2.drawContours(line_img, green, -1, (255, 0, 0), 3)
            for red in contours_red:
                line_img = cv2.drawContours(line_img, red, -1, (0, 255, 0), 3)
            line_img = cv2.circle(line_img, (poi[0][1], poi[0][2]), 5, (255, 0, 0), -1)
            # line_img = cv2.putText(line_img, str(angle.value), (0, int(camera_y * 0.12)), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

        # fps counter 
        counter += 1
        if (time.perf_counter() - fps_time > 1):
            fps = int(counter / (time.perf_counter() - fps_time))
            fps_time = time.perf_counter()
            counter = 0
        cv2.putText(line_img, str(fps), (int(camera_x * 0.92), int(camera_y * 0.05)), cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 255, 0), 1)
        cv2.imshow(line_img_name, line_img)
        # cv2.imshow("hsv", hsvImage)

        rawCapture.truncate(0)
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            terminate.value = True
            break
# line_loop()
# if (i == 1 and poi_x < camera_x * 0.1 and camera_y * 0.75 > poi_y > camera_y * 0.3) or (i == 2 and poi_x > camera_x * 0.9 and camera_y * 0.75 > poi_y > camera_y * 0.3) or poi_y < camera_y * 0.05:
