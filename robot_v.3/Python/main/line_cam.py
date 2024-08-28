import os
from multiprocessing import shared_memory

import cv2
from libcamera import controls
from numba import njit
from picamera2 import Picamera2
from skimage.metrics import structural_similarity
from ultralytics import YOLO

from Managers import Timer
from mp_manager import *

debug_mode = False

# Disable libcamera and Picamera2 logging
Picamera2.set_logging(Picamera2.ERROR)
os.environ["LIBCAMERA_LOG_LEVELS"] = "4"

camera_x = 448
camera_y = 252

calibration_square_size = 25

# These are not actually used, but are here for reference
black_min = np.array([0, 0, 0])

black_max_normal_top = np.array([90, 90, 90])
black_max_normal_bottom = np.array([135, 135, 135])

black_max_silver_validate_top_off = np.array([50, 50, 50])
black_max_silver_validate_bottom_off = np.array([48, 48, 48])

black_max_silver_validate_top_on = np.array([60, 60, 60])
black_max_silver_validate_bottom_on = np.array([80, 80, 80])

black_max_ramp_down_top = np.array([40, 40, 40])
black_max_zone = np.array([45, 45, 45])

green_min = np.array([40, 50, 45])
green_max = np.array([85, 255, 255])

green_min_zone = np.array([50, 50, 45])
green_max_zone = np.array([110, 255, 255])

red_min_1 = np.array([0, 100, 90])
red_max_1 = np.array([10, 255, 255])
red_min_2 = np.array([170, 100, 100])
red_max_2 = np.array([180, 255, 255])

red_min_1_zone = np.array([0, 100, 90])
red_max_1_zone = np.array([10, 255, 255])
red_min_2_zone = np.array([170, 100, 100])
red_max_2_zone = np.array([180, 255, 255])

multiple_bottom_side = camera_x / 2

timer = Timer()


def save_image(image):
    if not os.path.exists("../../Ai/datasets/images_to_annotate"):
        os.mkdir("../../Ai/datasets/images_to_annotate")
    num = len(os.listdir("../../Ai/datasets/images_to_annotate"))
    cv2.imwrite(f"../../Ai/datasets/images_to_annotate/{num:04d}.png", image)


def update_color_values():
    global black_max_normal_top, black_max_normal_bottom, black_max_silver_validate_top_off, black_max_silver_validate_bottom_off, black_max_silver_validate_top_on, black_max_silver_validate_bottom_on, black_max_ramp_down_top, black_max_zone, green_min, green_max, green_min_zone, green_max_zone, red_min_1, red_max_1, red_min_2, red_max_2, red_min_1_zone, red_max_1_zone, red_min_2_zone, red_max_2_zone

    black_max_normal_top = np.array(config_manager.read_variable('color_values_line', 'black_max_normal_top'))
    black_max_normal_bottom = np.array(config_manager.read_variable('color_values_line', 'black_max_normal_bottom'))
    black_max_silver_validate_top_off = np.array(config_manager.read_variable('color_values_line', 'black_max_silver_validate_top_off'))
    black_max_silver_validate_bottom_off = np.array(config_manager.read_variable('color_values_line', 'black_max_silver_validate_bottom_off'))
    black_max_silver_validate_top_on = np.array(config_manager.read_variable('color_values_line', 'black_max_silver_validate_top_on'))
    black_max_silver_validate_bottom_on = np.array(config_manager.read_variable('color_values_line', 'black_max_silver_validate_bottom_on'))
    black_max_ramp_down_top = np.array(config_manager.read_variable('color_values_line', 'black_max_ramp_down_top'))
    black_max_zone = np.array(config_manager.read_variable('color_values_line', 'black_max_zone'))

    green_min = np.array(config_manager.read_variable('color_values_line', 'green_min'))
    green_max = np.array(config_manager.read_variable('color_values_line', 'green_max'))
    green_min_zone = np.array(config_manager.read_variable('color_values_line', 'green_min_zone'))
    green_max_zone = np.array(config_manager.read_variable('color_values_line', 'green_max_zone'))

    red_min_1 = np.array(config_manager.read_variable('color_values_line', 'red_min_1'))
    red_max_1 = np.array(config_manager.read_variable('color_values_line', 'red_max_1'))
    red_min_2 = np.array(config_manager.read_variable('color_values_line', 'red_min_2'))
    red_max_2 = np.array(config_manager.read_variable('color_values_line', 'red_max_2'))

    red_min_1_zone = np.array(config_manager.read_variable('color_values_line', 'red_min_1_zone'))
    red_max_1_zone = np.array(config_manager.read_variable('color_values_line', 'red_max_1_zone'))
    red_min_2_zone = np.array(config_manager.read_variable('color_values_line', 'red_min_2_zone'))
    red_max_2_zone = np.array(config_manager.read_variable('color_values_line', 'red_max_2_zone'))


def check_contour_size(contours, contour_color="red", size=15000):
    if contour_color == "red":
        color = (0, 255, 0)
    elif contour_color == "green":
        color = (0, 0, 255)
    else:
        color = (255, 0, 0)

    for contour in contours:
        contour_size = cv2.contourArea(contour)

        if contour_size > size:
            x, y, w, h = cv2.boundingRect(contour)
            cv2.rectangle(cv2_img, (x, y), (x + w, y + h), color, 2)
            return True

    return False


def check_green(contours_grn, black_image):
    black_around_sign = np.zeros((len(contours_grn), 5), dtype=np.int16)  # [[b,t,l,r,lp], [b,t,l,r,lp]]

    for i, contour in enumerate(contours_grn):
        area = cv2.contourArea(contour)
        if area <= 2500:
            continue

        green_box = cv2.boxPoints(cv2.minAreaRect(contour))
        draw_box = np.intp(green_box)
        cv2.drawContours(cv2_img, [draw_box], -1, (0, 0, 255), 2)

        black_around_sign = check_black(black_around_sign, i, green_box, black_image.copy())

    turn_left, turn_right, left_bottom, right_bottom = determine_turn_direction(black_around_sign)

    if turn_left and not turn_right and not left_bottom:
        return "left"
    elif turn_right and not turn_left and not right_bottom:
        return "right"
    elif turn_left and turn_right and not (left_bottom and right_bottom):
        return "turn_around"
    else:
        return "straight"


@njit(cache=True)
def check_black(black_around_sign, i, green_box, black_image):
    green_box = green_box[green_box[:, 1].argsort()]

    marker_height = green_box[-1][1] - green_box[0][1]

    black_around_sign[i, 4] = int(green_box[2][1])

    # Bottom
    roi_b = black_image[int(green_box[2][1]):np.minimum(int(green_box[2][1] + (marker_height * 0.8)), camera_y), np.minimum(int(green_box[2][0]), int(green_box[3][0])):np.maximum(int(green_box[2][0]), int(green_box[3][0]))]
    if roi_b.size > 0:
        if np.mean(roi_b[:]) > 125:
            black_around_sign[i, 0] = 1

    # Top
    roi_t = black_image[np.maximum(int(green_box[1][1] - (marker_height * 0.8)), 0):int(green_box[1][1]), np.minimum(np.maximum(int(green_box[0][0]), 0), np.maximum(int(green_box[1][0]), 0)):np.maximum(np.maximum(int(green_box[0][0]), 0), np.maximum(int(green_box[1][0]), 0))]
    if roi_t.size > 0:
        if np.mean(roi_t[:]) > 125:
            black_around_sign[i, 1] = 1

    green_box = green_box[green_box[:, 0].argsort()]

    # Left
    roi_l = black_image[np.minimum(int(green_box[0][1]), int(green_box[1][1])):np.maximum(int(green_box[0][1]), int(green_box[1][1])), np.maximum(int(green_box[1][0] - (marker_height * 0.8)), 0):int(green_box[1][0])]
    if roi_l.size > 0:
        if np.mean(roi_l[:]) > 125:
            black_around_sign[i, 2] = 1

    # Right
    roi_r = black_image[np.minimum(int(green_box[2][1]), int(green_box[3][1])):np.maximum(int(green_box[2][1]), int(green_box[3][1])), int(green_box[2][0]):np.minimum(int(green_box[2][0] + (marker_height * 0.8)), camera_x)]
    if roi_r.size > 0:
        if np.mean(roi_r[:]) > 125:
            black_around_sign[i, 3] = 1

    return black_around_sign


def determine_turn_direction(black_around_sign):
    turn_left = False
    turn_right = False
    left_bottom = False
    right_bottom = False

    for i in black_around_sign:
        if np.sum(i[:4]) == 2:
            if i[1] == 1 and i[2] == 1:
                turn_right = True
                if i[4] > camera_y * 0.95:
                    right_bottom = True
            elif i[1] == 1 and i[3] == 1:
                turn_left = True
                if i[4] > camera_y * 0.95:
                    left_bottom = True

    return turn_left, turn_right, left_bottom, right_bottom


def determine_correct_line(contours_blk):
    global x_last, y_last
    candidates = np.zeros((len(contours_blk), 5), dtype=np.int32)
    off_bottom = 0

    for i, contour in enumerate(contours_blk):
        box = cv2.boxPoints(cv2.minAreaRect(contour))
        box = box[box[:, 1].argsort()[::-1]]  # Sort them by their y values and reverse
        bottom_y = box[0][1]
        y_mean = (np.clip(box[0][1], 0, camera_y) + np.clip(box[3][1], 0, camera_y)) / 2

        if box[0][1] >= (camera_y * 0.75):
            off_bottom += 1

        box = box[box[:, 0].argsort()]
        x_mean = (np.clip(box[0][0], 0, camera_x) + np.clip(box[3][0], 0, camera_x)) / 2
        x_y_distance = abs(x_last - x_mean) + abs(y_last - y_mean)  # Distance between the last x/y and current x/y

        candidates[i] = i, bottom_y, x_y_distance, x_mean, y_mean

    if off_bottom < 2:
        candidates = candidates[candidates[:, 1].argsort()[::-1]]  # Sort candidates by their bottom_y
    else:
        off_bottom_candidates = candidates[np.where(candidates[:, 1] >= (camera_y * 0.75))]
        candidates = off_bottom_candidates[off_bottom_candidates[:, 2].argsort()]

    if turn_dir.value == "left":
        x_last = np.clip(candidates[0][3] - 150, 0, camera_x)
    elif turn_dir.value == "right":
        x_last = np.clip(candidates[0][3] + 150, 0, camera_x)
    else:
        x_last = candidates[0][3]

    y_last = candidates[0][4]
    blackline = contours_blk[candidates[0][0]]
    blackline_crop = blackline[np.where(blackline[:, 0, 1] > camera_y * line_crop.value)]

    cv2.drawContours(cv2_img, blackline, -1, (255, 0, 0), 2)
    cv2.drawContours(cv2_img, blackline_crop, -1, (255, 255, 0), 2)

    cv2.circle(cv2_img, (int(x_last), int(y_last)), 3, (0, 0, 255), -1)

    return blackline, blackline_crop


@njit(cache=True)
def calculate_angle_numba(blackline, blackline_crop, last_bottom_point, average_line_point):
    max_gap = 1
    max_line_width = camera_x * .19

    poi_no_crop = np.zeros((4, 2), dtype=np.int32)  # [t, l, r, b]

    # Top without crop
    blackline_y_min = np.amin(blackline[:, :, 1])
    blackline_top = blackline[np.where(blackline[:, 0, 1] == blackline_y_min)][:, :, 0]

    blackline_top = blackline_top[blackline_top[:, 0].argsort()]
    blackline_top_gap_fill = (blackline_top + max_gap + 1)[:-1]

    blackline_gap_mask = blackline_top_gap_fill < blackline_top[1:]

    top_mean = (int(np.mean(blackline_top)), blackline_y_min)

    if np.sum(blackline_gap_mask) == 1:
        gap_index = np.where(blackline_gap_mask)[0][0]

        if blackline_top[:gap_index].size > 0 and blackline_top[gap_index:].size > 0:
            top_mean_l = int(np.mean(blackline_top[:gap_index]))
            top_mean_r = int(np.mean(blackline_top[gap_index:]))

            top_mean = (top_mean_l, blackline_y_min) if np.abs(top_mean_l - average_line_point) < np.abs(top_mean_r - average_line_point) else (top_mean_r, blackline_y_min)

    poi_no_crop[0] = [top_mean[0], top_mean[1]]

    # Bottom without crop
    blackline_y_max = np.amax(blackline[:, :, 1])
    blackline_bottom = blackline[np.where(blackline[:, 0, 1] == blackline_y_max)][:, :, 0]
    blackline_bottom = blackline_bottom[blackline_bottom[:, 0].argsort()]
    blackline_bottom_gap_fill = (blackline_bottom + max_gap + 1)[:-1]

    blackline_gap_mask = blackline_bottom_gap_fill < blackline_bottom[1:]

    bottom_point_mean = (int(np.mean(blackline_bottom)), blackline_y_max)

    if np.sum(blackline_gap_mask) == 1:
        gap_index = np.where(blackline_gap_mask)[0][0]

        if blackline_bottom[:gap_index].size > 0 and blackline_bottom[gap_index:].size > 0:
            bottom_mean_l = int(np.mean(blackline_bottom[:gap_index]))
            bottom_mean_r = int(np.mean(blackline_bottom[gap_index:]))

            if np.abs(bottom_mean_l - bottom_mean_r) > 80:
                if np.abs(bottom_mean_l - last_bottom_point) < np.abs(bottom_mean_r - last_bottom_point):
                    bottom_point_mean = (bottom_mean_l, blackline_y_max)
                    bottom_mean = (bottom_mean_r, blackline_y_max)
                else:
                    bottom_point_mean = (bottom_mean_r, blackline_y_max)
                    bottom_mean = (bottom_mean_l, blackline_y_max)

                poi_no_crop[3] = [bottom_mean[0], bottom_mean[1]]

    bottom_point = [bottom_point_mean[0], bottom_point_mean[1]]

    # Left without crop
    blackline_x_min = np.amin(blackline[:, :, 0])
    blackline_left = blackline[np.where(blackline[:, 0, 0] == blackline_x_min)]
    left_mean = (blackline_x_min, int(np.mean(blackline_left[:, :, 1])))
    poi_no_crop[1] = [left_mean[0], left_mean[1]]

    # Right without crop
    blackline_x_max = np.amax(blackline[:, :, 0])
    blackline_right = blackline[np.where(blackline[:, 0, 0] == blackline_x_max)]
    right_mean = (blackline_x_max, int(np.mean(blackline_right[:, :, 1])))
    poi_no_crop[2] = [right_mean[0], right_mean[1]]

    poi = np.zeros((3, 2), dtype=np.int32)  # [t, l, r]
    is_crop = blackline_crop.size > 0

    max_black_top = False

    if is_crop:
        # Top
        blackline_y_min = np.amin(blackline_crop[:, :, 1])
        blackline_top = blackline_crop[np.where(blackline_crop[:, 0, 1] == blackline_y_min)][:, :, 0]
        top_mean = (int(np.mean(blackline_top)), blackline_y_min)
        poi[0] = [top_mean[0], top_mean[1]]

        blackline_top = blackline_top[blackline_top[:, 0].argsort()]
        max_black_top = bool(np.abs(blackline_top[0] - blackline_top[-1]) > max_line_width)

        # Left
        blackline_x_min = np.amin(blackline_crop[:, :, 0])
        blackline_left = blackline_crop[np.where(blackline_crop[:, 0, 0] == blackline_x_min)]
        left_mean = (blackline_x_min, int(np.mean(blackline_left[:, :, 1])))
        poi[1] = [left_mean[0], left_mean[1]]

        # Right
        blackline_x_max = np.amax(blackline_crop[:, :, 0])
        blackline_right = blackline_crop[np.where(blackline_crop[:, 0, 0] == blackline_x_max)]
        right_mean = (blackline_x_max, int(np.mean(blackline_right[:, :, 1])))
        poi[2] = [right_mean[0], right_mean[1]]

    return poi, poi_no_crop, is_crop, max_black_top, bottom_point


def calculate_angle(blackline, blackline_crop, average_line_angle, turn_direction, last_bottom_point, average_line_point, entry):
    global multiple_bottom_side

    poi, poi_no_crop, is_crop, max_black_top, bottom_point = calculate_angle_numba(blackline, blackline_crop, last_bottom_point, average_line_point)

    black_top = poi_no_crop[0][1] < camera_y * .1

    multiple_bottom = not (poi_no_crop[3][0] == 0 and poi_no_crop[3][1] == 0)

    black_l_high = poi_no_crop[1][1] < camera_y * .5
    black_r_high = poi_no_crop[2][1] < camera_y * .5

    if entry:
        final_poi = poi_no_crop[0]

    elif not timer.get_timer("multiple_bottom"):
        final_poi = [multiple_bottom_side, camera_y]

    elif turn_direction in ["left", "right"]:
        index = 1 if turn_direction == "left" else 2
        final_poi = poi[index] if is_crop else poi_no_crop[index]

    else:
        if black_top:
            final_poi = poi[0] if is_crop and not max_black_top else poi_no_crop[0]

            if (poi_no_crop[1][0] < camera_x * 0.02 and poi_no_crop[1][1] > camera_y * (line_crop.value * .75)) or (poi_no_crop[2][0] > camera_x * 0.98 and poi_no_crop[2][1] > camera_y * (line_crop.value * .75)):
                final_poi = poi_no_crop[0]

                if black_l_high or black_r_high:
                    near_high_index = 0

                    if black_l_high and not black_r_high:
                        near_high_index = 1

                    elif not black_l_high and black_r_high:
                        near_high_index = 2

                    elif black_l_high and black_r_high:
                        if np.abs(poi_no_crop[1][0] - average_line_point) < np.abs(poi_no_crop[2][0] - average_line_point):
                            near_high_index = 1
                        else:
                            near_high_index = 2

                    if np.abs(poi_no_crop[near_high_index][0] - average_line_point) < np.abs(poi_no_crop[0][0] - average_line_point):
                        final_poi = poi_no_crop[near_high_index]

        else:
            final_poi = poi[0] if is_crop else poi_no_crop[0]

            if poi_no_crop[1][0] < camera_x * 0.02 and poi_no_crop[2][0] > camera_x * 0.98 and timer.get_timer("multiple_side_r") and timer.get_timer("multiple_side_l"):
                if average_line_angle >= 0:
                    index = 2
                    timer.set_timer("multiple_side_r", .6)
                else:
                    index = 1
                    timer.set_timer("multiple_side_l", .6)

                final_poi = poi[index] if is_crop else poi_no_crop[index]

            elif not timer.get_timer("multiple_side_l"):
                final_poi = poi[1] if is_crop else poi_no_crop[1]

            elif not timer.get_timer("multiple_side_r"):
                final_poi = poi[2] if is_crop else poi_no_crop[2]

            elif poi_no_crop[1][0] < camera_x * 0.02:
                final_poi = poi[1] if is_crop else poi_no_crop[1]

            elif poi_no_crop[2][0] > camera_x * 0.98:
                final_poi = poi[2] if is_crop else poi_no_crop[2]

            elif multiple_bottom and timer.get_timer("multiple_bottom"):
                if poi_no_crop[3][0] < bottom_point[0]:
                    final_poi = [0, camera_y]
                    multiple_bottom_side = 0
                else:
                    final_poi = [camera_x, camera_y]
                    multiple_bottom_side = camera_x
                timer.set_timer("multiple_bottom", .6)

    return int((final_poi[0] - camera_x / 2) / (camera_x / 2) * 180), final_poi, bottom_point


def get_gap_angle(box):
    box = box[box[:, 1].argsort()]

    vector = box[0] - box[1]
    angle = np.arccos(np.dot(vector, [1, 0]) / (np.linalg.norm(vector) * np.linalg.norm([1, 0]))) * 180 / np.pi
    angle = angle if box[0][0] < box[1][0] else -angle

    if angle == 180:
        angle = 0

    return box[0], box[1], angle


def get_silver_angle(box):
    box = box[box[:, 0].argsort()]

    left_points = box[:2]
    right_points = box[2:]

    left_points = left_points[left_points[:, 1].argsort()]
    right_points = right_points[right_points[:, 1].argsort()]

    vector = left_points[0] - right_points[0]
    angle = np.arccos(np.dot(vector, [1, 0]) / (np.linalg.norm(vector) * np.linalg.norm([1, 0]))) * 180 / np.pi
    angle = -angle if left_points[0][1] < right_points[0][1] else angle
    if angle == 180:
        angle = 0

    return left_points[0], right_points[0], angle


def get_exit_angle(box):
    box = box[box[:, 0].argsort()]

    left_points = box[:2]
    right_points = box[2:]

    left_points = left_points[left_points[:, 1].argsort()]
    right_points = right_points[right_points[:, 1].argsort()]

    vector = left_points[-1] - right_points[-1]
    angle = np.arccos(np.dot(vector, [1, 0]) / (np.linalg.norm(vector) * np.linalg.norm([1, 0]))) * 180 / np.pi
    angle = -angle if left_points[-1][1] < right_points[-1][1] else angle
    if angle == 180:
        angle = 0

    return left_points[-1], right_points[-1], angle


def average_direction(turn_direction):
    turn_dir_num = 0

    if turn_direction == "left":
        turn_dir_num = -1
    elif turn_direction == "right":
        turn_dir_num = 1

    return turn_dir_num


def calc_silver_angle(silver_image):

    silver_first_row = silver_image[0, :].copy()
    white_pixel_index = np.where(silver_first_row == 255)[0]
    if len(white_pixel_index) > 0:
        first_white_pixel_index = white_pixel_index[0]
        last_white_pixel_index = white_pixel_index[-1]

        cv2.rectangle(silver_image, (first_white_pixel_index, 0), (last_white_pixel_index, camera_y), 0, -1)

    silver_last_row = silver_image[-1, :].copy()
    white_pixel_index = np.where(silver_last_row == 255)[0]
    if len(white_pixel_index) > 0:
        first_white_pixel_index = white_pixel_index[0]
        last_white_pixel_index = white_pixel_index[-1]

        cv2.rectangle(silver_image, (first_white_pixel_index, 0), (last_white_pixel_index, camera_y), 0, -1)

    cv2.rectangle(silver_image, (0, 0), (20, camera_y), 0, -1)
    cv2.rectangle(silver_image, (camera_x - 20, 0), (camera_x, camera_y), 0, -1)

    contours_silver, _ = cv2.findContours(silver_image, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)

    # save_image(silver_image)
    if len(contours_silver) > 0:
        largest_silver_contour = max(contours_silver, key=cv2.contourArea)
        cv2.drawContours(cv2_img, [np.int0(cv2.boxPoints(cv2.minAreaRect(largest_silver_contour)))], 0, (255, 255, 0), 2)
        p1, p2, angle = get_silver_angle(cv2.boxPoints(cv2.minAreaRect(largest_silver_contour)))
        if p1[1] < camera_y * 0.95 and p2[1] < camera_y * 0.95:
            silver_angle.value = angle
            cv2.line(cv2_img, (int(p1[0]), int(p1[1])), (int(p2[0]), int(p2[1])), (0, 255, 0), 2)
    else:
        silver_angle.value = -181


########################################################################################################################
# Line Cam Loop
########################################################################################################################


def line_cam_loop():
    global cv2_img, x_last, y_last, time_line_angle

    model = YOLO('../../Ai/models/silver_zone_entry/silver_classify_s.onnx', task='classify')

    x_last = camera_x / 2
    y_last = camera_y / 2

    bottom_y = camera_y

    time_line_angle = empty_time_arr()
    time_turn_direction = empty_time_arr()

    time_last_bottom_point_x = empty_time_arr()
    time_last_average_line_point = empty_time_arr()

    camera = Picamera2()

    mode = camera.sensor_modes[0]
    camera.configure(camera.create_video_configuration(sensor={'output_size': mode['size'], 'bit_depth': mode['bit_depth']}))

    camera.start()
    camera.set_controls({"AfMode": controls.AfModeEnum.Manual, "LensPosition": 6.5, "FrameDurationLimits": (1000000 // 50, 1000000 // 50)})  # {"AfMode": controls.AfModeEnum.Manual, "LensPosition": 0.4} {"AfMode": controls.AfModeEnum.Continuous, "AfSpeed": controls.AfSpeedEnum.Fast}
    time.sleep(0.1)

    if not debug_mode:
        shm_cam1 = shared_memory.SharedMemory(name="shm_cam_1", create=True, size=338688)

    calibration_saved = True
    update_color_values()

    # Kernal for noise reduction
    kernal = np.ones((3, 3), np.uint8)

    # FPS counter
    fps_time = time.perf_counter()
    counter = 0
    fps = 0

    # FPS limiter 
    max_frames_zone = 20
    max_frames_line = 90
    fps_limit_time = time.perf_counter()

    last_image = np.zeros((camera_y, camera_x), dtype=np.uint8)

    timer.set_timer("image_similarity", .5)
    timer.set_timer("multiple_bottom", .05)
    timer.set_timer("multiple_side_l", .05)
    timer.set_timer("multiple_side_r", .05)
    timer.set_timer("right_marker", .05)
    timer.set_timer("left_marker", .05)
    timer.set_timer("right_marker_up", .05)
    timer.set_timer("left_marker_up", .05)

    do_inference_counter = 10
    check_similarity_counter = 0
    check_similarity_limit = 30

    while not terminate.value:
        raw_capture = camera.capture_array()
        raw_capture = cv2.resize(raw_capture, (camera_x, camera_y))
        cv2_img = cv2.cvtColor(raw_capture, cv2.COLOR_RGBA2BGR)

        frame_limit = max_frames_zone if objective.value == "zone" and (zone_status.value == "begin" or zone_status.value == "find_balls" or zone_status.value == "pickup_ball") else max_frames_line
        if objective.value == "follow_line" and not rotation_y.value in ["ramp_down", "ramp_up"]:
            do_inference_limit = 7
        elif objective.value == "follow_line" and rotation_y.value in ["ramp_down", "ramp_up"]:
            do_inference_limit = 4
        else:
            do_inference_limit = 10

        if time.perf_counter() - fps_limit_time > 1 / frame_limit:
            fps_limit_time = time.perf_counter()

            if calibrate_color_status.value == "none":

                # Silver AI prediction
                if objective.value == "follow_line":
                    if do_inference_counter >= do_inference_limit:
                        results = model.predict(raw_capture, imgsz=128, conf=0.4, workers=4, verbose=False)
                        result = results[0].numpy()

                        confidences = result.probs.top5conf
                        silver_value.value = confidences[0] if result.probs.top1 == 1 else confidences[1]  # 0 = Line, 1 = Silver
                        do_inference_counter = 0

                    do_inference_counter += 1
                    if silver_value.value > .5:
                        cv2.circle(cv2_img, (10, camera_y - 10), 5, (100, 100, 100), -1, cv2.LINE_AA)

                if objective.value == "follow_line":
                    hsv_image = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2HSV)
                    green_image = cv2.inRange(hsv_image, green_min, green_max)
                    red_image = cv2.inRange(hsv_image, red_min_1, red_max_1) + cv2.inRange(hsv_image, red_min_2, red_max_2)

                    # Adjust black calibration for zone entry
                    if line_status.value in ["check_silver", "position_entry", "position_entry_1"]:
                        black_image = cv2.inRange(cv2_img, black_min, black_max_silver_validate_bottom_off)
                        black_image[0:int(camera_y * .7), 0:camera_x] = cv2.inRange(cv2_img, black_min, black_max_silver_validate_top_off)[0:int(camera_y * .7), 0:camera_x]

                    elif line_status.value == "position_entry_2":
                        black_image = cv2.inRange(cv2_img, black_min, black_max_silver_validate_bottom_on)
                        black_image[0:int(camera_y * .4), 0:camera_x] = cv2.inRange(cv2_img, black_min, black_max_silver_validate_top_on)[0:int(camera_y * .4), 0:camera_x]

                    else:
                        black_image = cv2.inRange(cv2_img, black_min, black_max_normal_bottom)
                        black_image[0:int(camera_y * .4), 0:camera_x] = cv2.inRange(cv2_img, black_min, black_max_normal_top)[0:int(camera_y * .4), 0:camera_x]

                    black_image -= green_image
                    black_image[black_image < 2] = 0

                    # Change black_max to black_max_ramp_down_top if the top section of the image is too dark
                    dark_ahead = False
                    black_mean = round(np.mean(black_image[0:int(camera_y * .25), 0:camera_x]), 2)
                    if black_mean > 90 and not line_status.value == "check_silver":
                        black_image_2 = cv2.inRange(cv2_img, black_min, black_max_ramp_down_top)
                        black_image_2 -= green_image
                        black_image_2[black_image_2 < 2] = 0

                        black_mean_2 = round(np.mean(black_image_2[0:int(camera_y * .25), 0:camera_x]), 2)

                        if black_mean_2 + 30 < black_mean:  # 20
                            cv2.circle(cv2_img, (10, 10), 5, (0, 0, 0), -1, cv2.LINE_AA)
                            black_image[0:int(camera_y * .4), 0:camera_x] = black_image_2[0:int(camera_y * .4), 0:camera_x]
                            dark_ahead = True

                    ramp_ahead.value = dark_ahead

                    black_average.value = np.mean(black_image[:])

                    # Check für image similarity
                    if check_similarity_counter >= check_similarity_limit:
                        line_similarity.value = structural_similarity(black_image, last_image)
                        last_image = black_image.copy()
                        check_similarity_counter = 0
                    check_similarity_counter += 1

                    # Cut out certain parts of the image
                    if line_status.value == "obstacle_avoid" or line_status.value == "obstacle_detected":
                        if rotation_y.value == "none":
                            cv2.rectangle(black_image, (0, 0), (camera_x, int(camera_y * .35)), 0, -1)
                        if obstacle_direction.value == "l":
                            cv2.rectangle(black_image, (0, 0), (int(camera_x * .75), camera_y), 0, -1)
                        elif obstacle_direction.value == "r":
                            cv2.rectangle(black_image, (int(camera_x * .25), 0), (camera_x, camera_y), 0, -1)
                    elif line_status.value == "obstacle_orientate":
                        cv2.rectangle(black_image, (0, 0), (camera_x, int(camera_y * .45)), 0, -1)

                    if line_status.value == "gap_avoid":
                        cv2.rectangle(black_image, (0, 0), (int(camera_x * .35), camera_y), 0, -1)
                        cv2.rectangle(black_image, (int(camera_x * .65), 0), (camera_x, camera_y), 0, -1)

                    if bottom_y < camera_y * .95 and black_average.value < 21 and line_status.value == "line_detected":
                        cv2.rectangle(black_image, (0, 0), (int(camera_x * .25), camera_y), 0, -1)
                        cv2.rectangle(black_image, (int(camera_x * .75), 0), (camera_x, camera_y), 0, -1)

                    # Noise reduction
                    if line_status.value == "position_entry_2":
                        black_image = cv2.erode(black_image, kernal, iterations=1)
                        black_image = cv2.dilate(black_image, kernal, iterations=11)
                        black_image = cv2.erode(black_image, kernal, iterations=9)
                    elif line_status.value == "gap_avoid":
                        black_image = cv2.erode(black_image, kernal, iterations=5)
                        black_image = cv2.dilate(black_image, kernal, iterations=8)
                    else:
                        black_image = cv2.erode(black_image, kernal, iterations=5)
                        black_image = cv2.dilate(black_image, kernal, iterations=17) # Previous values: 12 | 16
                        black_image = cv2.erode(black_image, kernal, iterations=9)  # Previous values: 4 | 8

                    green_image = cv2.erode(green_image, kernal, iterations=1)
                    green_image = cv2.dilate(green_image, kernal, iterations=11)
                    green_image = cv2.erode(green_image, kernal, iterations=9)

                    red_image = cv2.erode(red_image, kernal, iterations=1)
                    red_image = cv2.dilate(red_image, kernal, iterations=11)
                    red_image = cv2.erode(red_image, kernal, iterations=9)

                    # Calculate the angle of the silver line
                    if line_status.value == "position_entry_1":
                        silver_black_image = black_image.copy()

                    if line_status.value == "position_entry_2":
                        silver_image = black_image.copy() - silver_black_image.copy()
                        silver_image[silver_image < 2] = 0
                        calc_silver_angle(silver_image)

                    # Find contours in the image
                    contours_grn, _ = cv2.findContours(green_image, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
                    contours_red, _ = cv2.findContours(red_image, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
                    contours_blk, _ = cv2.findContours(black_image, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)

                    blk_contour_area = np.array([cv2.contourArea(i) for i in contours_blk])
                    blk_mask = blk_contour_area > min_line_size.value
                    contours_blk = [c for c, m in zip(contours_blk, blk_mask) if m]

                    # Check for red line
                    red_detected.value = check_contour_size(contours_red)

                    # Check for green turn signs
                    if len(contours_grn) > 0:
                        turn_direction = check_green(contours_grn, black_image)
                    else:
                        turn_direction = "straight"

                    time_turn_direction = add_time_value(time_turn_direction, average_direction(turn_direction))
                    avg_turn_dir = get_time_average(time_turn_direction, .2)

                    if avg_turn_dir > .1 and not rotation_y.value == "ramp_up":
                        timer.set_timer("right_marker", .5)
                    elif avg_turn_dir > .1 and rotation_y.value == "ramp_up":
                        timer.set_timer("right_marker_up", .8)
                    elif avg_turn_dir < -.1 and not rotation_y.value == "ramp_up":
                        timer.set_timer("left_marker", .5)
                    elif avg_turn_dir < -.1 and rotation_y.value == "ramp_up":
                        timer.set_timer("left_marker_up", .8)

                    if (not timer.get_timer("right_marker") or not timer.get_timer("right_marker_up")) and not turn_direction == "turn_around" and avg_turn_dir >= 0 and rotation_y.value != "ramp_up":
                        turn_dir.value = "right"
                        line_crop.value = .45
                    elif (not timer.get_timer("right_marker") or not timer.get_timer("right_marker_up")) and not turn_direction == "turn_around" and avg_turn_dir >= 0 and rotation_y.value == "ramp_up":
                        turn_dir.value = "right"
                        line_crop.value = .75
                    elif (not timer.get_timer("left_marker") or not timer.get_timer("left_marker_up")) and not turn_direction == "turn_around" and avg_turn_dir <= 0 and rotation_y.value != "ramp_up":
                        turn_dir.value = "left"
                        line_crop.value = .45
                    elif (not timer.get_timer("left_marker") or not timer.get_timer("left_marker_up")) and not turn_direction == "turn_around" and avg_turn_dir <= 0 and rotation_y.value == "ramp_up":
                        turn_dir.value = "left"
                        line_crop.value = .75
                    else:
                        turn_dir.value = turn_direction
                        line_crop.value = .75 if rotation_y.value == "ramp_up" or not timer.get_timer("was_ramp_up") else .48

                    # Determine the correct line
                    if len(contours_blk) > 0:
                        line_detected.value = True
                        blackline, black_line_crop = determine_correct_line(contours_blk)
                        line_size.value = cv2.contourArea(blackline)

                        # Calculate the gap angle 
                        if line_status.value == "gap_detected":
                            p1, p2, angle = get_gap_angle(cv2.boxPoints(cv2.minAreaRect(blackline)))
                            if p1[1] < camera_y * 0.95 and p2[1] < camera_y * 0.95:
                                gap_angle.value = angle

                                center_gap_ponit = (p1 - p2) / 2 + p2

                                gap_center_x.value = int((center_gap_ponit[0] - camera_x / 2) / (camera_x / 2) * 180)
                                gap_center_y.value = center_gap_ponit[1]

                                cv2.line(cv2_img, (int(p1[0]), int(p1[1])), (int(p2[0]), int(p2[1])), (0, 255, 0), 2)
                                cv2.circle(cv2_img, (int(center_gap_ponit[0]), int(center_gap_ponit[1])), 5, (0, 255, 0), 1, cv2.LINE_AA)

                        else:
                            gap_angle.value = -181
                            gap_center_x.value = -181
                            gap_center_y.value = -1

                        # Calculate the angle to turn
                        last_bottom_point_x = get_time_average(time_last_bottom_point_x, .15)
                        last_average_line_point = get_time_average(time_last_average_line_point, .15)

                        line_angle.value, poi, bottom_point = calculate_angle(blackline, black_line_crop, get_time_average(time_line_angle, .3), turn_dir.value, last_bottom_point_x, last_average_line_point, entry=line_status.value == "position_entry")
                        line_angle_y.value = poi[1]

                        time_line_angle = add_time_value(time_line_angle, line_angle.value)
                        time_last_bottom_point_x = add_time_value(time_last_bottom_point_x, bottom_point[0])

                        if bottom_point[0] != poi[0] and bottom_point[1] != poi[1]:
                            slope = (bottom_point[1] - poi[1]) / (bottom_point[0] - poi[0])
                            x = min(max(poi[0] + (0 - poi[1]) / slope, 0), camera_x)
                        else:
                            x = poi[0]

                        time_last_average_line_point = add_time_value(time_last_average_line_point, x)

                        bottom_y = bottom_point[1]

                        cv2.circle(cv2_img, (int(last_average_line_point), 0), 5, (0, 255, 255), 1, cv2.LINE_AA)
                        cv2.circle(cv2_img, poi, 5, (0, 0, 255), 1, cv2.LINE_AA)
                        cv2.circle(cv2_img, bottom_point, 5, (255, 255, 0), 1, cv2.LINE_AA)

                    else:
                        line_detected.value = False
                        line_angle.value = 0
                        line_size.value = 0
                        line_angle_y.value = -1
                        gap_angle.value = -181
                        gap_center_x.value = -181
                        gap_center_y.value = -1


                ########################################################################################################################
                # Zone Loop
                ########################################################################################################################

                elif objective.value == "zone":
                    hsv_image = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2HSV)
                    green_image = cv2.inRange(hsv_image, green_min_zone, green_max_zone)
                    red_image = cv2.inRange(hsv_image, red_min_1_zone, red_max_1_zone) + cv2.inRange(hsv_image, red_min_2_zone, red_max_2_zone)

                    if zone_status.value in ["exit", "deposit_red", "deposit_green"]:  # With LEDs on
                        black_image = cv2.inRange(cv2_img, black_min, black_max_normal_bottom)
                        black_image[0:int(camera_y * .4), 0:camera_x] = cv2.inRange(cv2_img, black_min, black_max_normal_top)[0:int(camera_y * .4), 0:camera_x]

                        black_image -= green_image
                        black_image[black_image < 2] = 0

                        black_image -= red_image
                        black_image[black_image < 2] = 0
                    else:
                        black_image = cv2.inRange(cv2_img, black_min, black_max_zone)

                    black_average.value = np.mean(black_image[:])

                    # Noise reduction
                    black_image = cv2.erode(black_image, kernal, iterations=5)
                    black_image = cv2.dilate(black_image, kernal, iterations=8)

                    green_image = cv2.erode(green_image, kernal, iterations=5)
                    green_image = cv2.dilate(green_image, kernal, iterations=8)

                    red_image = cv2.erode(red_image, kernal, iterations=5)
                    red_image = cv2.dilate(red_image, kernal, iterations=8)

                    # Find contours in the image
                    contours_grn, _ = cv2.findContours(green_image, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
                    contours_red, _ = cv2.findContours(red_image, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
                    contours_blk, _ = cv2.findContours(black_image, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)

                    blk_contour_area = np.array([cv2.contourArea(i) for i in contours_blk])
                    blk_mask = blk_contour_area > min_line_size.value
                    contours_blk = [c for c, m in zip(contours_blk, blk_mask) if m]

                    zone_found_black.value = check_contour_size(contours_blk, contour_color="black", size=16500)
                    zone_found_green.value = check_contour_size(contours_grn, contour_color="green", size=9000)
                    zone_found_red.value = check_contour_size(contours_red, contour_color="red", size=9000)

                    if zone_status.value == "get_exit_angle":
                        if len(contours_blk) > 0:
                            largest_black_contour = max(contours_blk, key=cv2.contourArea)
                            cv2.drawContours(cv2_img, [np.int0(cv2.boxPoints(cv2.minAreaRect(largest_black_contour)))], 0, (255, 255, 0), 2)
                            p1, p2, angle = get_exit_angle(cv2.boxPoints(cv2.minAreaRect(largest_black_contour)))
                            if p1[1] < camera_y * 0.95 and p2[1] < camera_y * 0.95:
                                exit_angle.value = angle
                                cv2.line(cv2_img, (int(p1[0]), int(p1[1])), (int(p2[0]), int(p2[1])), (0, 255, 0), 2)
                        else:
                            exit_angle.value = -181


            ########################################################################################################################
            # Calibration
            ########################################################################################################################

            elif calibrate_color_status.value == "calibrate" and not (calibration_color.value == "z-g" or calibration_color.value == "z-r"):

                # (x1,y1,x2,y2)
                center_calibration_square = [int(camera_x / 2 - calibration_square_size), int(camera_y / 2 - calibration_square_size), int(camera_x / 2 + calibration_square_size), int(camera_y / 2 + calibration_square_size)]
                top_calibration_square = [int(camera_x / 2 - calibration_square_size), int(camera_y / 4 - calibration_square_size), int(camera_x / 2 + calibration_square_size), int(camera_y / 4 + calibration_square_size)]
                top_edge_calibration_square_small = [int(camera_x // 2 - calibration_square_size * (2 / 3)), 0, int(camera_x / 2 + calibration_square_size * (2 / 3)), int(2 * calibration_square_size * (2 / 3))]
                bottom_edge_calibration_square = [int(camera_x / 2 - calibration_square_size), int(camera_y - calibration_square_size * 2), int(camera_x / 2 + calibration_square_size), camera_y]

                if calibration_color.value in ["l-rz", "l-rl"]:
                    color = (0, 0, 255)
                elif calibration_color.value in ["l-gz", "l-gl"]:
                    color = (0, 255, 0)
                else:
                    color = (0, 0, 0)

                if calibration_color.value in ["l-gl", "l-rl", "l-bz", "l-bvl"]:
                    cv2.rectangle(cv2_img, (center_calibration_square[0], center_calibration_square[1]), (center_calibration_square[2], center_calibration_square[3]), color, 2)
                elif calibration_color.value in ["l-gz", "l-rz"]:
                    cv2.rectangle(cv2_img, (top_calibration_square[0], top_calibration_square[1]), (top_calibration_square[2], top_calibration_square[3]), color, 2)
                elif calibration_color.value in ["l-bd"]:
                    cv2.rectangle(cv2_img, (top_edge_calibration_square_small[0], top_edge_calibration_square_small[1]), (top_edge_calibration_square_small[2], top_edge_calibration_square_small[3]), color, 2)
                elif calibration_color.value in ["l-bn", "l-bv"]:
                    cv2.rectangle(cv2_img, (top_calibration_square[0], top_calibration_square[1]), (top_calibration_square[2], top_calibration_square[3]), color, 2)
                    cv2.rectangle(cv2_img, (bottom_edge_calibration_square[0], bottom_edge_calibration_square[1]), (bottom_edge_calibration_square[2], bottom_edge_calibration_square[3]), color, 2)

                calibration_saved = False

            elif calibrate_color_status.value == "check" and not (calibration_color.value == "z-g" or calibration_color.value == "z-r"):
                if not calibration_saved:

                    if calibration_color.value == "l-gl":
                        average_color = find_average_color(cv2.cvtColor(cv2_img, cv2.COLOR_BGR2HSV)[center_calibration_square[1]:center_calibration_square[3], center_calibration_square[0]:center_calibration_square[2]])

                        c_green_min = np.clip(np.rint(np.array([average_color[0] - 20, 95, average_color[2] - 60])), 0, 255)
                        c_green_max = np.clip(np.rint([average_color[0] + 20, 255, 255]), 0, 255)

                        config_manager.write_variable('color_values_line', 'green_min', [int(c_green_min[0]), int(c_green_min[1]), int(c_green_min[2])])
                        config_manager.write_variable('color_values_line', 'green_max', [int(c_green_max[0]), int(c_green_max[1]), int(c_green_max[2])])

                    elif calibration_color.value == "l-rl":
                        average_color = find_average_color(cv2.cvtColor(cv2_img, cv2.COLOR_BGR2HSV)[center_calibration_square[1]:center_calibration_square[3], center_calibration_square[0]:center_calibration_square[2]])

                        c_red_min = np.clip(np.rint(np.array([100, 90])), 0, 255)
                        c_red_max = np.clip(np.rint([255, 255]), 0, 255)

                        config_manager.write_variable('color_values_line', 'red_min_1', [0, int(c_red_min[0]), int(c_red_min[1])])
                        config_manager.write_variable('color_values_line', 'red_max_1', [10, int(c_red_max[0]), int(c_red_max[1])])
                        config_manager.write_variable('color_values_line', 'red_min_2', [170, int(c_red_min[0]), 100])
                        config_manager.write_variable('color_values_line', 'red_max_2', [180, int(c_red_max[0]), int(c_red_max[1])])

                    elif calibration_color.value == "l-bz":
                        average_color = find_average_color(cv2_img[center_calibration_square[1]:center_calibration_square[3], center_calibration_square[0]:center_calibration_square[2]])

                        c_black_max_zone = np.clip(np.rint(np.array([average_color[0] + 20, average_color[1] + 20, average_color[2] + 20])), 0, 255)

                        config_manager.write_variable('color_values_line', 'black_max_zone', [int(c_black_max_zone[0]), int(c_black_max_zone[1]), int(c_black_max_zone[2])])

                    elif calibration_color.value == "l-gz":
                        average_color = find_average_color(cv2.cvtColor(cv2_img, cv2.COLOR_BGR2HSV)[top_calibration_square[1]:top_calibration_square[3], top_calibration_square[0]:top_calibration_square[2]])

                        c_green_min_zone = np.clip(np.rint(np.array([average_color[0] - 20, 95, average_color[2] - 60])), 0, 255)
                        c_green_max_zone = np.clip(np.rint(np.array([average_color[0] + 20, 255, 255])), 0, 255)

                        config_manager.write_variable('color_values_line', 'green_min_zone', [int(c_green_min_zone[0]), int(c_green_min_zone[1]), int(c_green_min_zone[2])])
                        config_manager.write_variable('color_values_line', 'green_max_zone', [int(c_green_max_zone[0]), int(c_green_max_zone[1]), int(c_green_max_zone[2])])

                    elif calibration_color.value == "l-rz":
                        average_color = find_average_color(cv2.cvtColor(cv2_img, cv2.COLOR_BGR2HSV)[top_calibration_square[1]:top_calibration_square[3], top_calibration_square[0]:top_calibration_square[2]])

                        c_red_min_1_zone = np.clip(np.rint(np.array([100, 90])), 0, 255)
                        c_red_max_1_zone = np.clip(np.rint(np.array([255, 255])), 0, 255)

                        config_manager.write_variable('color_values_line', 'red_min_1_zone', [0, int(c_red_min_1_zone[0]), int(c_red_min_1_zone[1])])
                        config_manager.write_variable('color_values_line', 'red_max_1_zone', [10, int(c_red_max_1_zone[0]), int(c_red_max_1_zone[1])])
                        config_manager.write_variable('color_values_line', 'red_min_2_zone', [170, int(c_red_min_1_zone[0]), 100])
                        config_manager.write_variable('color_values_line', 'red_max_2_zone', [180, int(c_red_max_1_zone[0]), int(c_red_max_1_zone[1])])

                    elif calibration_color.value == "l-bd":
                        average_color = find_average_color(cv2_img[top_edge_calibration_square_small[1]:top_edge_calibration_square_small[3], top_edge_calibration_square_small[0]:top_edge_calibration_square_small[2]])

                        c_black_max_ramp_down_top = np.clip(np.rint(np.array([average_color[0] + 15, average_color[1] + 15, average_color[2] + 15])), 0, 255)

                        config_manager.write_variable('color_values_line', 'black_max_ramp_down_top', [int(c_black_max_ramp_down_top[0]), int(c_black_max_ramp_down_top[1]), int(c_black_max_ramp_down_top[2])])

                    elif calibration_color.value == "l-bn":
                        average_color_1 = find_average_color(cv2_img[top_calibration_square[1]:top_calibration_square[3], top_calibration_square[0]:top_calibration_square[2]])
                        average_color_2 = find_average_color(cv2_img[bottom_edge_calibration_square[1]:bottom_edge_calibration_square[3], bottom_edge_calibration_square[0]:bottom_edge_calibration_square[2]])

                        c_black_max_normal_top = np.clip(np.rint(np.array([average_color_1[0] + 65, average_color_1[1] + 65, average_color_1[2] + 65])), 0, 255)
                        c_black_max_normal_bottom = np.clip(np.rint(np.array([average_color_2[0] + 75, average_color_2[1] + 75, average_color_2[2] + 75])), 0, 255)

                        config_manager.write_variable('color_values_line', 'black_max_normal_top', [int(c_black_max_normal_top[0]), int(c_black_max_normal_top[1]), int(c_black_max_normal_top[2])])
                        config_manager.write_variable('color_values_line', 'black_max_normal_bottom', [int(c_black_max_normal_bottom[0]), int(c_black_max_normal_bottom[1]), int(c_black_max_normal_bottom[2])])

                    elif calibration_color.value == "l-bv":
                        average_color_1 = find_average_color(cv2_img[top_calibration_square[1]:top_calibration_square[3], top_calibration_square[0]:top_calibration_square[2]])
                        average_color_2 = find_average_color(cv2_img[bottom_edge_calibration_square[1]:bottom_edge_calibration_square[3], bottom_edge_calibration_square[0]:bottom_edge_calibration_square[2]])

                        c_black_max_silver_validate_top_off = np.clip(np.rint(np.array([average_color_1[0] + 30, average_color_1[1] + 30, average_color_1[2] + 30])), 0, 255)
                        c_black_max_silver_validate_bottom_off = np.clip(np.rint(np.array([average_color_2[0] + 30, average_color_2[1] + 30, average_color_2[2] + 30])), 0, 255)

                        config_manager.write_variable('color_values_line', 'black_max_silver_validate_top_off', [int(c_black_max_silver_validate_top_off[0]), int(c_black_max_silver_validate_top_off[1]), int(c_black_max_silver_validate_top_off[2])])
                        config_manager.write_variable('color_values_line', 'black_max_silver_validate_bottom_off', [int(c_black_max_silver_validate_bottom_off[0]), int(c_black_max_silver_validate_bottom_off[1]), int(c_black_max_silver_validate_bottom_off[2])])

                    elif calibration_color.value == "l-bvl":
                        average_color = find_average_color(cv2_img[center_calibration_square[1]:center_calibration_square[3], center_calibration_square[0]:center_calibration_square[2]])

                        c_black_max_silver_validate_top_on = np.clip(np.rint(np.array([average_color[0], average_color[1], average_color[2]])), 0, 255)
                        c_black_max_silver_validate_bottom_on = np.clip(np.rint(np.array([average_color[0] + 30, average_color[1] + 30, average_color[2] + 30])), 0, 255)

                        config_manager.write_variable('color_values_line', 'black_max_silver_validate_top_on', [int(c_black_max_silver_validate_top_on[0]), int(c_black_max_silver_validate_top_on[1]), int(c_black_max_silver_validate_top_on[2])])
                        config_manager.write_variable('color_values_line', 'black_max_silver_validate_bottom_on', [int(c_black_max_silver_validate_bottom_on[0]), int(c_black_max_silver_validate_bottom_on[1]), int(c_black_max_silver_validate_bottom_on[2])])

                    update_color_values()
                    calibration_saved = True
                    continue

                if calibration_color.value == "l-gl":
                    cv2_img = cv2.inRange(cv2.cvtColor(cv2_img.copy(), cv2.COLOR_BGR2HSV), green_min, green_max)

                    cv2_img = cv2.erode(cv2_img, kernal, iterations=1)
                    cv2_img = cv2.dilate(cv2_img, kernal, iterations=11)
                    cv2_img = cv2.erode(cv2_img, kernal, iterations=9)

                elif calibration_color.value == "l-rl":
                    cv2_img = cv2.inRange(cv2.cvtColor(cv2_img, cv2.COLOR_BGR2HSV), red_min_1, red_max_1) + cv2.inRange(cv2.cvtColor(cv2_img, cv2.COLOR_BGR2HSV), red_min_2, red_max_2)

                    cv2_img = cv2.erode(cv2_img, kernal, iterations=1)
                    cv2_img = cv2.dilate(cv2_img, kernal, iterations=11)
                    cv2_img = cv2.erode(cv2_img, kernal, iterations=9)

                elif calibration_color.value == "l-bz":
                    cv2_img = cv2.inRange(cv2_img, black_min, black_max_zone)

                elif calibration_color.value == "l-gz":
                    cv2_img = cv2.inRange(cv2.cvtColor(cv2_img, cv2.COLOR_BGR2HSV), green_min_zone, green_max_zone)

                elif calibration_color.value == "l-rz":
                    cv2_img = cv2.inRange(cv2.cvtColor(cv2_img, cv2.COLOR_BGR2HSV), red_min_1_zone, red_max_1_zone) + cv2.inRange(cv2.cvtColor(cv2_img, cv2.COLOR_BGR2HSV), red_min_2_zone, red_max_2_zone)

                elif calibration_color.value == "l-bd":
                    black_img = cv2.inRange(cv2_img, black_min, black_max_normal_bottom)
                    black_img[0:int(camera_y * .4), 0:camera_x] = cv2.inRange(cv2_img, black_min, black_max_ramp_down_top)[0:int(camera_y * .4), 0:camera_x]

                    hsv_image = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2HSV)
                    green_image = cv2.inRange(hsv_image, green_min, green_max)

                    black_img -= green_image
                    black_img[black_img < 2] = 0

                    black_img = cv2.erode(black_img, kernal, iterations=5)
                    black_img = cv2.dilate(black_img, kernal, iterations=8)

                    cv2_img = black_img.copy()

                elif calibration_color.value == "l-bn":
                    black_img = cv2.inRange(cv2_img, black_min, black_max_normal_bottom)
                    black_img[0:int(camera_y * .4), 0:camera_x] = cv2.inRange(cv2_img, black_min, black_max_normal_top)[0:int(camera_y * .4), 0:camera_x]

                    hsv_image = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2HSV)
                    green_image = cv2.inRange(hsv_image, green_min, green_max)

                    black_img -= green_image
                    black_img[black_img < 2] = 0

                    black_img = cv2.erode(black_img, kernal, iterations=5)
                    black_img = cv2.dilate(black_img, kernal, iterations=8)

                    cv2_img = black_img.copy()

                elif calibration_color.value == "l-bv":
                    black_img = cv2.inRange(cv2_img, black_min, black_max_silver_validate_bottom_off)
                    black_img[0:int(camera_y * .7), 0:camera_x] = cv2.inRange(cv2_img, black_min, black_max_silver_validate_top_off)[0:int(camera_y * .7), 0:camera_x]

                    hsv_image = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2HSV)
                    green_image = cv2.inRange(hsv_image, green_min, green_max)

                    black_img -= green_image
                    black_img[black_img < 2] = 0

                    black_img = cv2.erode(black_img, kernal, iterations=5)
                    black_img = cv2.dilate(black_img, kernal, iterations=8)

                    cv2_img = black_img.copy()

                elif calibration_color.value == "l-bvl":
                    black_img = cv2.inRange(cv2_img, black_min, black_max_silver_validate_bottom_on)
                    black_img[0:int(camera_y * .4), 0:camera_x] = cv2.inRange(cv2_img, black_min, black_max_silver_validate_top_on)[0:int(camera_y * .4), 0:camera_x]

                    hsv_image = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2HSV)
                    green_image = cv2.inRange(hsv_image, green_min, green_max)

                    black_img -= green_image
                    black_img[black_img < 2] = 0

                    black_img = cv2.erode(black_img, kernal, iterations=1)
                    black_img = cv2.dilate(black_img, kernal, iterations=11)
                    black_img = cv2.erode(black_img, kernal, iterations=9)

                    cv2_img = black_img.copy()

                cv2_img = cv2.cvtColor(cv2_img, cv2.COLOR_GRAY2BGR)

            # FPS Counter
            counter += 1
            if time.perf_counter() - fps_time > 1:
                fps = int(counter / (time.perf_counter() - fps_time))
                fps_time = time.perf_counter()
                counter = 0

            cv2.putText(cv2_img, str(fps), (int(camera_x * 0.92), int(camera_y * 0.05)), cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 255, 0), 1, cv2.LINE_AA)

            # Checking the shared memory buffer size of the image
            # print(cv2_img.size)

            if debug_mode:
                cv2.imshow("Line Camera", cv2_img)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            else:
                buf = np.ndarray(cv2_img.shape, dtype=cv2_img.dtype, buffer=shm_cam1.buf)
                buf[:] = cv2_img[:]

    if not debug_mode:
        shm_cam1.close()
        shm_cam1.unlink()


if debug_mode:
    line_cam_loop()
