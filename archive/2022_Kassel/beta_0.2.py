import time

import RPi.GPIO as GPIO
import cv2
import numpy as np
import serial
from picamera import PiCamera
from picamera.array import PiRGBArray

# camera resolution 
camera_x = 368
camera_y = 208

# accuracy when follwing the line
accuracy = 20

# error and angle multiplier 
em = 1
am = 0.5

roi_y_min = camera_y * 0.4  # 0.5
roi_y_max = camera_y * 1  # 0.9

# distinguish between line and crossing
max_line_width = 130

# motor setup
in1 = 23  # forwards right
in2 = 24  # backwards right
in3 = 27  # forwards left
in4 = 22  # backwards right
ena = 12  # speed right
enb = 13  # speed left

# correction due to different motor speeds
motorACorrection = 1
motorBCorrection = 1

# GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(in1, GPIO.OUT)
GPIO.setup(in2, GPIO.OUT)
GPIO.setup(in3, GPIO.OUT)
GPIO.setup(in4, GPIO.OUT)
GPIO.setup(ena, GPIO.OUT)
GPIO.setup(enb, GPIO.OUT)

# PWM setup
pa = GPIO.PWM(ena, 1000)
pa.start(0)
pb = GPIO.PWM(enb, 1000)
pb.start(0)

# camera Setup
camera = PiCamera()
camera.resolution = (camera_x, camera_y)
camera.rotation = 180  # camera is mounted upside down
rawCapture = PiRGBArray(camera, size=(camera_x, camera_y))

time.sleep(0.1)

# serial commucation with Arduino 
ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
ser.reset_input_buffer()

global sensor1  # distance sensor 50cm
sensor1 = -1
global sensor2  # distance sensor 130cm
sensor2 = -1
global sensor3  # rotation sensor
sensor3 = 0


def check_serial():
    global sensor1
    global sensor2
    global sensor3

    while ser.in_waiting > 0:
        serial = ser.readline().decode('utf-8').rstrip()

        if len(serial.split(" ")) == 2:
            if serial.startswith("S1 "):
                sensor1 = int(serial.split(" ", 1)[1])
            elif serial.startswith("S2 "):
                sensor2 = int(serial.split(" ", 1)[1])
            elif serial.startswith("A1 "):
                sensor3 = int(serial.split(" ", 1)[1])


def motor_steer(speed_l, speed_r, steering, wait_time=0):
    # stop
    if steering > camera_x * 10:
        pa.ChangeDutyCycle(0)
        pb.ChangeDutyCycle(0)
        GPIO.output(in1, GPIO.LOW)
        GPIO.output(in2, GPIO.LOW)
        GPIO.output(in3, GPIO.LOW)
        GPIO.output(in4, GPIO.LOW)

        if not wait_time == 0:
            time.sleep(wait_time)

            pa.ChangeDutyCycle(0)
            pb.ChangeDutyCycle(0)
            GPIO.output(in1, GPIO.LOW)
            GPIO.output(in2, GPIO.LOW)
            GPIO.output(in3, GPIO.LOW)
            GPIO.output(in4, GPIO.LOW)

        return

    elif steering < -camera_x * 10:
        pa.ChangeDutyCycle(0)
        pb.ChangeDutyCycle(0)
        GPIO.output(in1, GPIO.HIGH)
        GPIO.output(in2, GPIO.LOW)
        GPIO.output(in3, GPIO.HIGH)
        GPIO.output(in4, GPIO.LOW)
        pa.ChangeDutyCycle(speed_r * motorACorrection)
        pb.ChangeDutyCycle(speed_l * motorBCorrection)

        if not wait_time == 0:
            time.sleep(wait_time)

            pa.ChangeDutyCycle(0)
            pb.ChangeDutyCycle(0)
            GPIO.output(in1, GPIO.LOW)
            GPIO.output(in2, GPIO.LOW)
            GPIO.output(in3, GPIO.LOW)
            GPIO.output(in4, GPIO.LOW)

        return

    # straight
    elif accuracy > steering > -accuracy:
        pa.ChangeDutyCycle(0)
        pb.ChangeDutyCycle(0)
        GPIO.output(in1, GPIO.LOW)
        GPIO.output(in2, GPIO.HIGH)
        GPIO.output(in3, GPIO.LOW)
        GPIO.output(in4, GPIO.HIGH)
        pa.ChangeDutyCycle(speed_r * motorACorrection)
        pb.ChangeDutyCycle(speed_l * motorBCorrection)

        if not wait_time == 0:
            time.sleep(wait_time)

            pa.ChangeDutyCycle(0)
            pb.ChangeDutyCycle(0)
            GPIO.output(in1, GPIO.LOW)
            GPIO.output(in2, GPIO.LOW)
            GPIO.output(in3, GPIO.LOW)
            GPIO.output(in4, GPIO.LOW)

        return
    # left
    elif steering < -accuracy:
        pa.ChangeDutyCycle(0)
        pb.ChangeDutyCycle(0)
        GPIO.output(in1, GPIO.LOW)
        GPIO.output(in2, GPIO.HIGH)
        GPIO.output(in3, GPIO.HIGH)
        GPIO.output(in4, GPIO.LOW)
        pa.ChangeDutyCycle(min(speed_r, 80) * motorACorrection)
        pb.ChangeDutyCycle(min(speed_l, 80) * motorBCorrection)

        if not wait_time == 0:
            time.sleep(wait_time)

            pa.ChangeDutyCycle(0)
            pb.ChangeDutyCycle(0)
            GPIO.output(in1, GPIO.LOW)
            GPIO.output(in2, GPIO.LOW)
            GPIO.output(in3, GPIO.LOW)
            GPIO.output(in4, GPIO.LOW)

        return
    # right
    elif steering > accuracy:
        pa.ChangeDutyCycle(0)
        pb.ChangeDutyCycle(0)
        GPIO.output(in1, GPIO.HIGH)
        GPIO.output(in2, GPIO.LOW)
        GPIO.output(in3, GPIO.LOW)
        GPIO.output(in4, GPIO.HIGH)
        pa.ChangeDutyCycle(min(speed_r, 80) * motorACorrection)
        pb.ChangeDutyCycle(min(speed_l, 80) * motorBCorrection)

        if not wait_time == 0:
            time.sleep(wait_time)

            pa.ChangeDutyCycle(0)
            pb.ChangeDutyCycle(0)
            GPIO.output(in1, GPIO.LOW)
            GPIO.output(in2, GPIO.LOW)
            GPIO.output(in3, GPIO.LOW)
            GPIO.output(in4, GPIO.LOW)

        return


global obstacle_counter
obstacle_counter = 0
global obstacle
obstacle = False


def avoid_obstacle():
    global obstacle_counter
    obstacle_counter = obstacle_counter + 1
    global obstacle

    if obstacle_counter == 1:
        motor_steer(speed, speed, -camera_x * 11, 0.15)  # drive backward
        motor_steer(speed, speed, accuracy + 1, 1.4)  # rotate left
    else:
        motor_steer(0, 100, accuracy - 1)


def turn():
    motor_steer(speed, speed, accuracy - 1, 0.7)  # drive forward
    motor_steer(speed, speed, -accuracy - 1, 3.25)  # rotate 180 degrees left


# global is_zone
# is_zone = False
# global zone_counter
# zone_counter = 0

# def zone():
#     global zone_counter
#     global is_zone
#     is_zone = True

#     if zone_counter == 0 or zone_counter == 1:        
#         motor_steer(speed, speed, accuracy - 1) # drive forward
#         if -1 < sensor1 < 90 and -1 < sensor2 < 70:
#             motor_steer(speed, speed, -camera_x * 11, 0.15) # drive backward
#             motor_steer(speed, speed, accuracy + 1, 3) # rotate left 180
#             motor_steer(60, 60, -camera_x * 11, 10) # drive backward
#             motor_steer(speed, speed, accuracy - 1, 0.4) # drive forward
#             motor_steer(speed, speed, accuracy + 1, 1.4) # rotate left 90 
#             zone_counter = zone_counter + 1
#     elif zone_counter == 2:
#         motor_steer(speed, speed, accuracy - 0.5) # drive forward
#         motor_steer(speed, speed, accuracy + 1, 1.4) # rotate left 90 
#         zone_counter = 3
#     elif zone_counter == 3:
#         motor_steer(speed, speed, accuracy + 1, 1.4) # rotate right 90
#         motor_steer(speed, speed, accuracy - 0.5) # drive forward
#         motor_steer(speed, speed, accuracy + 1, 1.4) # rotate left 90 

global no_line_counter
no_line_counter = 0


# global is_zone_counter
# is_zone_counter = 0

def no_line():
    global no_line_counter
    # global is_zone_counter
    no_line_counter = no_line_counter + 1

    if no_line_counter == 6:
        motor_steer(speed, speed, accuracy - 1, 0.3)  # drive forward
    elif no_line_counter == 7:
        motor_steer(speed, speed, -camera_x * 11, 0.3)  # drive backwards
    elif no_line_counter == 8:
        motor_steer(speed, speed, accuracy + 1, 0.7)  # rotate right
    elif no_line_counter == 9:
        motor_steer(speed, speed, accuracy + 1, 0.6)  # rotate right
    elif no_line_counter == 10:
        motor_steer(speed, speed, -accuracy - 1, 1.2)  # rotate left
    elif no_line_counter == 11:
        motor_steer(speed, speed, -accuracy - 1, 0.6)  # rotate left
    elif no_line_counter == 12:
        motor_steer(speed, speed, -accuracy - 1, 0.5)  # rotate left
    elif no_line_counter == 13:
        motor_steer(speed, speed, accuracy + 1, 1.3)  # rotate right
    elif no_line_counter == 14:
        motor_steer(speed, speed, accuracy - 1, 0.15)  # drive forward
    elif no_line_counter == 15:
        motor_steer(speed, speed, accuracy - 1, 0.15)  # drive forward
        no_line_counter = 0

    # if is_zone_counter == 3:
    #     zone()


# fps counter
fps_time = time.time()
counter = 0
fps = 0

x_last = camera_x / 2  # savin the x value of the last line center
line_center = np.array([[float(0), float(camera_x / 2)]])  # savin the x values of the last line centers

average_left = np.array([[float(time.time()), float(0)]])  # saving the last turning values left
average_right = np.array([[float(time.time()), float(0)]])  # saving the last turning values right

start_time = time.time()
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    image = frame.array
    blackline = cv2.inRange(image, (0, 0, 0), (85, 85, 85))  # definig colour for the line
    greensign = cv2.inRange(image, (0, 50, 0), (100, 160, 100))  # definig colour for the green signs
    kernal = np.ones((3, 3), np.uint8)  # removing noise
    blackline = cv2.erode(blackline, kernal, iterations=5)
    blackline = cv2.dilate(blackline, kernal, iterations=9)
    greensign = cv2.erode(greensign, kernal, iterations=5)
    greensign = cv2.dilate(greensign, kernal, iterations=9)
    contours_blk, hierarchy_blk = cv2.findContours(blackline, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)  # get every black contour in the image
    contours_grn, hierarchy_grn = cv2.findContours(greensign, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)  # get every green sign in the image

    check_serial()

    if sensor3 > 20:
        speed = 55
        cv2.putText(image, "ramp down", (int(camera_x * 0.7), int(camera_y * 0.65)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
    elif sensor3 < -20:
        speed = 95
        cv2.putText(image, "ramp up", (int(camera_x * 0.8), int(camera_y * 0.65)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
    else:
        speed = 80

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

        blackbox = contours_blk[candidates[0][0]]

        box = cv2.boxPoints(cv2.minAreaRect(blackbox))  # get the corners of blackbox
        box = box[box[:, 1].argsort()[::-1]]  # sort by y values and reverse
        x_last = (box[0][0] + box[1][0]) / 2  # save new x_last value

        # calculate green signs   
        # getting the position of the black line relativ to the green sign      ! fix needed for left + right! #roi = image[int(max(4, green_box[0][0])):int(min(camera_x, max(5, green_box[3][0]))), int(max(4, green_box[0][1])):int(min(camera_y, max(5, green_box[3][1] + (camera_y * 0.1))))]
        position_black = [[]]
        lowest_green_sign = 0
        for i in range(len(contours_grn)):
            black_detected = False
            if cv2.contourArea(contours_grn[i]) > 1000:
                green_box = cv2.boxPoints(cv2.minAreaRect(contours_grn[i]))

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

        # distinguish intersections and normal blackline 
        intersection = False
        box = cv2.boxPoints(cv2.minAreaRect(blackbox))  # get the corners of blackbox
        box = box[box[:, 1].argsort()[::-1]]  # sort by y values and reverse

        if abs(box[0][0] - box[1][0]) > max_line_width and box[2][1] + box[3][1] < camera_x * 0.6:  # intersection
            intersection = True
            cv2.putText(image, "intersection", (int(camera_x * 0.75), int(camera_y * 0.8)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)

            average_line_center = np.mean(line_center[:, 1])

            if (left and not right):
                blackbox = blackbox[np.where(blackbox[:, :, 0] > 0)]
                blackbox = blackbox[np.where(blackbox[:, 0] < average_line_center - (max_line_width / 2))]
                cv2.putText(image, "turn left", (int(camera_x * 0.8), int(camera_y * 0.95)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

                if lowest_green_sign > camera_y * 0.9:
                    motor_steer(speed, speed, accuracy - 1, 0.7)  # drive forward
                    motor_steer(speed, speed, -accuracy - 1, 1.4)  # rotate left

            elif (not left and right):
                blackbox = blackbox[np.where(blackbox[:, :, 0] > average_line_center + (max_line_width / 2))]
                blackbox = blackbox[np.where(blackbox[:, 0] < camera_x)]
                cv2.putText(image, "turn right", (int(camera_x * 0.8), int(camera_y * 0.95)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

                if lowest_green_sign > camera_y * 0.9:
                    motor_steer(speed, speed, accuracy - 1, 0.7)  # drive forward
                    motor_steer(speed, speed, accuracy + 1, 1.4)  # rotate right

            elif turn_around:
                cv2.putText(image, "turn around", (int(camera_x * 0.8), int(camera_y * 0.95)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

                if lowest_green_sign > camera_y * 0.9:
                    turn()

            elif straight:
                blackbox = blackbox[np.where(blackbox[:, :, 1] > roi_y_min)]
                blackbox = blackbox[np.where(blackbox[:, 1] < roi_y_max)]

        else:
            (x_min, y_min), (w_min, h_min), ang = cv2.minAreaRect(blackbox)
            line_center = np.append(line_center, [[float(time.time() - start_time), float(round(x_min, 2))]], axis=0)
            line_center = line_center[np.where(line_center[:, 0] > ((time.time() - start_time) - 0.15))]  # saving every y_min value of the last 0.15 seconds before an intersection

            # cut out the region of interest 
            blackbox = blackbox[np.where(blackbox[:, :, 1] > roi_y_min)]
            blackbox = blackbox[np.where(blackbox[:, 1] < roi_y_max)]

        # using the processed blackbox to calculate steering 
        blackbox = cv2.minAreaRect(blackbox)
        if (len(blackbox) > 0):  # if the is any contour within the region of interst

            # calculating the angle between blackline and y axis 
            (x_min, y_min), (w_min, h_min), ang = blackbox

            if ang < -45:
                ang = 90 + ang
            if w_min < h_min and ang > 0:
                ang = (90 - ang) * -1
            if w_min > h_min and ang < 0:
                ang = 90 + ang

            if 90 >= ang > 0:
                ang = ang - 90
            elif 0 > ang >= -90:
                ang = 90 + ang

            ang = int(ang)
            error = int(x_min - camera_x / 2)  # calculating the distance between the center of blackline and the center of the screen

            if intersection and straight:
                error = 0
                ang = ang * 0.5

            # minimum area of black to follow
            roi = image[int(roi_y_min): int(roi_y_max), int(0): int(camera_x)]
            black = cv2.inRange(roi, (0, 0, 0), (90, 90, 90))

            box = cv2.boxPoints(blackbox)  # get the corners of blackbox
            box = box[box[:, 1].argsort()[::-1]]  # sort by y values and reverse

            if 120 > np.mean(black[:]) > 20:
                if no_line_counter > 0:
                    if abs(box[2][0] - box[3][0]) > camera_x * 0.7:
                        if not obstacle:
                            no_line()
                    else:
                        no_line_counter = 0
                else:
                    obstacle_counter = 0
                    obstacle = False
                    if intersection:
                        motor_steer(50, 50, (error * em + ang * am))
                    else:
                        motor_steer(speed, speed, (error * em + ang * am))
            else:
                if not obstacle:
                    no_line()

            # visualations 
            cv2.drawContours(image, contours_blk, -1, (200, 50, 150), 3)  # visualise black contours
            cv2.drawContours(image, [np.int0(cv2.boxPoints(blackbox))], 0, (255, 0, 0), 3)
            cv2.line(image, (int(x_min), int(roi_y_min)), (int(x_min), int(roi_y_max)), (0, 0, 255), 3)

            cv2.putText(image, "angle", (0, int(camera_y * 0.2)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
            cv2.putText(image, str(int(ang)), (0, int(camera_y * 0.12)), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
            cv2.putText(image, "error", (0, int(camera_y * 0.45)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
            cv2.putText(image, str(int(error)), (0, int(camera_y * 0.37)), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

        else:
            if not obstacle:
                no_line()
    else:
        if not obstacle:
            no_line()

    if -1 < sensor1 < 90 and -1 < sensor2 < 70:
        avoid_obstacle()
        obstacle = True
    elif obstacle:
        avoid_obstacle()

    # fps counter 
    counter += 1
    if ((time.time() - fps_time) > 1):
        fps = int(counter / (time.time() - fps_time))
        counter = 0
        fps_time = time.time()
    cv2.putText(image, str(fps), (int(camera_x * 0.92), int(camera_y * 0.1)), cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 0, 255), 1)

    cv2.putText(image, "sensor 50", (0, int(camera_y * 0.7)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
    cv2.putText(image, str(sensor1), (0, int(camera_y * 0.62)), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
    cv2.putText(image, "sensor 130", (0, int(camera_y * 0.95)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
    cv2.putText(image, str(sensor2), (0, int(camera_y * 0.87)), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

    cv2.imshow("image", image)  # show the processed picture
    rawCapture.truncate(0)
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break

GPIO.cleanup()  # cleanup GPIO pins
