import os
from multiprocessing import shared_memory

import cv2
from picamera2 import Picamera2
from skimage.metrics import structural_similarity
from ultralytics import YOLO
from ultralytics.utils.plotting import colors

from Managers import Timer
from mp_manager import *

camera_width = 640
camera_height = 480

calibration_square_size = 25
horizontal_center = camera_width // 2

text_pos = np.array([int(camera_width * 0.96), int(camera_height * 0.04)])

# These are not actually used, but are here for reference
green_min = np.array([40, 50, 35])
green_max = np.array([90, 255, 255])

red_min_1 = np.array([0, 100, 70])
red_max_1 = np.array([10, 255, 255])
red_min_2 = np.array([170, 100, 70])
red_max_2 = np.array([180, 255, 255])

# Kernal for noise reduction
kernal = np.ones((3, 3), np.uint8)

timer = Timer()


def save_image(image):
    if not os.path.exists("../../Ai/datasets/images_to_annotate/zone_images"):
        os.mkdir("../../Ai/datasets/images_to_annotate/zone_images")
    num = len(os.listdir("../../Ai/datasets/images_to_annotate/zone_images"))
    cv2.imwrite(f"../../Ai/datasets/images_to_annotate/zone_images/{num:04d}.png", image)


def update_color_values():
    global green_min, green_max, red_min_1, red_max_1, red_min_2, red_max_2

    green_min = np.array(config_manager.read_variable('color_values_zone', 'green_min'))
    green_max = np.array(config_manager.read_variable('color_values_zone', 'green_max'))

    red_min_1 = np.array(config_manager.read_variable('color_values_zone', 'red_min_1'))
    red_max_1 = np.array(config_manager.read_variable('color_values_zone', 'red_max_1'))
    red_min_2 = np.array(config_manager.read_variable('color_values_zone', 'red_min_2'))
    red_max_2 = np.array(config_manager.read_variable('color_values_zone', 'red_max_2'))


def check_contours(contours, image, color, size=5000):
    if len(contours) > 0:
        largest_contour = max(contours, key=cv2.contourArea)

        if cv2.contourArea(largest_contour) > size:
            x, y, w, h = cv2.boundingRect(largest_contour)
            cv2.rectangle(image, (x, y), (x + w, y + h), color, 2)

            box_width_center = x + w // 2

            return (box_width_center - horizontal_center) / horizontal_center * 180, abs(h)

    return -181, 0


def get_green_contours(image):
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    green_image = cv2.inRange(hsv_image, green_min, green_max)

    green_image = cv2.erode(green_image, kernal, iterations=5)
    green_image = cv2.dilate(green_image, kernal, iterations=8)

    contours_green, _ = cv2.findContours(green_image, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    return contours_green


def get_red_contours(image):
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    red_image = cv2.inRange(hsv_image, red_min_1, red_max_1) + cv2.inRange(hsv_image, red_min_2, red_max_2)

    red_image = cv2.erode(red_image, kernal, iterations=5)
    red_image = cv2.dilate(red_image, kernal, iterations=8)

    contours_red, _ = cv2.findContours(red_image, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    return contours_red


########################################################################################################################
# Zone Cam Loop
########################################################################################################################


def zone_cam_loop():
    model = YOLO('../../Ai/models/ball_zone_s/ball_detect_s_edgetpu.tflite', task='detect')

    crop_percentage = 0.45
    crop_height = int(camera_height * crop_percentage)

    camera = Picamera2(1)
    camera.start()

    shm_cam2 = shared_memory.SharedMemory(name="shm_cam_2", create=True, size=506880)

    calibration_saved = True

    # fps counter
    fps_time = time.perf_counter()
    counter = 0
    fps = 0

    # fps limiter 
    max_frames_zone = 30
    max_frames_line = 1
    fps_limit_time = time.perf_counter()

    last_best_box = None
    last_image = np.zeros((264, camera_width), dtype=np.uint8)
    check_similarity_counter = 0
    check_similarity_limit = 10

    update_color_values()
    while not terminate.value:
        raw_capture = camera.capture_array()
        raw_capture = raw_capture[crop_height:, :]
        cv2_img = cv2.cvtColor(raw_capture, cv2.COLOR_RGBA2BGR)

        if capture_image.value:
            save_image(cv2_img)
            capture_image.value = False

        frame_limit = max_frames_zone if objective.value == "zone" or not calibrate_color_status.value == "none" else max_frames_line

        if time.perf_counter() - fps_limit_time > 1 / frame_limit:
            fps_limit_time = time.perf_counter()

            if calibrate_color_status.value == "none":
                if objective.value == "zone":
                    if check_similarity_counter >= check_similarity_limit:
                        grey_image = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2GRAY)
                        zone_similarity.value = structural_similarity(grey_image, last_image)
                        last_image = grey_image.copy()
                        check_similarity_counter = 0
                    check_similarity_counter += 1

                    if zone_status.value == "begin" or zone_status.value == "find_balls" or zone_status.value == "pickup_ball":
                        results = model.predict(cv2_img, imgsz=(512, 224), conf=0.3, iou=0.2, agnostic_nms=True, workers=4, verbose=False)  # verbose=True to enable debug info

                        result = results[0].numpy()

                        boxes = []
                        for box in result.boxes:
                            x1, y1, x2, y2 = box.xyxy[0].astype(int)
                            class_id = box.cls[0].astype(int)
                            name = result.names[class_id]
                            confidence = box.conf[0].astype(float)

                            width = x2 - x1
                            height = y2 - y1
                            area = width * height
                            distance = (x1 + width // 2) - horizontal_center
                            boxes.append([area, distance, name, width])

                            color = colors(class_id, True)
                            cv2.rectangle(cv2_img, (x1, y1), (x2, y2), color, 2)
                            cv2.putText(cv2_img, f"{name}: {confidence:.2f}", (x1, y1 - 5), cv2.FONT_HERSHEY_DUPLEX, 0.5, color, 1, cv2.LINE_AA)

                        if len(boxes) > 0:
                            best_box = max(boxes, key=lambda x: x[0])
                            if last_best_box is not None:
                                best_box = min(boxes, key=lambda x: abs(x[1] - last_best_box[1]))

                            last_best_box = best_box
                            ball_distance.value = best_box[1]
                            ball_type.value = str.lower(str(best_box[2]))
                            ball_width.value = best_box[3]
                        else:
                            last_best_box = None
                            ball_distance.value = 0
                            ball_type.value = "none"
                            ball_width.value = -1

                    elif zone_status.value == "deposit_green":
                        contours_green = get_green_contours(cv2_img)
                        corner_distance.value, corner_size.value = check_contours(contours_green, cv2_img, (0, 0, 255))

                    elif zone_status.value == "deposit_red":
                        contours_red = get_red_contours(cv2_img)
                        corner_distance.value, corner_size.value = check_contours(contours_red, cv2_img, (0, 255, 0))


            elif calibrate_color_status.value == "calibrate" and (calibration_color.value == "z-r" or calibration_color.value == "z-g"):
                color = (0, 0, 255) if calibration_color.value == "z-r" else (0, 255, 0)

                cv2.rectangle(cv2_img, (int(camera_width // 2 - calibration_square_size), int(((camera_height * crop_percentage) / 2) - calibration_square_size)), (int(camera_width / 2 + calibration_square_size), int(((camera_height * crop_percentage) / 2)) + calibration_square_size), color, 2)
                calibration_saved = False

            elif calibrate_color_status.value == "check" and (calibration_color.value == "z-r" or calibration_color.value == "z-g"):
                if not calibration_saved:
                    average_color = find_average_color(cv2.cvtColor(cv2_img, cv2.COLOR_BGR2HSV)[int(((camera_height * crop_percentage) / 2) - calibration_square_size):int(((camera_height * crop_percentage) / 2) + calibration_square_size), int(camera_width / 2 - calibration_square_size):int(camera_width / 2 + calibration_square_size)])

                    if calibration_color.value == "z-g":
                        c_green_min = np.clip(np.rint(np.array([average_color[0] - 25, average_color[1] - 60, average_color[2] - 60])), 0, 255)
                        c_green_max = np.clip(np.rint(np.array([average_color[0] + 25, average_color[1] + 60, average_color[2] + 70])), 0, 255)

                        config_manager.write_variable('color_values_zone', 'green_min', [int(c_green_min[0]), int(c_green_min[1]), int(c_green_min[2])])
                        config_manager.write_variable('color_values_zone', 'green_max', [int(c_green_max[0]), int(c_green_max[1]), int(c_green_max[2])])

                        update_color_values()

                    elif calibration_color.value == "z-r":
                        c_red_min = np.clip(np.rint(np.array([average_color[1] - 70, average_color[2] - 40])), 0, 255)
                        c_red_max = np.clip(np.rint(np.array([average_color[1] + 70, average_color[2] + 150])), 0, 255)

                        config_manager.write_variable('color_values_zone', 'red_min_1', [0, int(c_red_min[0]), int(c_red_min[1])])
                        config_manager.write_variable('color_values_zone', 'red_max_1', [10, int(c_red_max[0]), int(c_red_max[1])])
                        config_manager.write_variable('color_values_zone', 'red_min_2', [170, int(c_red_min[0]), int(c_red_min[1])])
                        config_manager.write_variable('color_values_zone', 'red_max_2', [180, int(c_red_max[0]), int(c_red_max[1])])

                        update_color_values()

                    calibration_saved = True
                    continue

                if calibration_color.value == "z-g":
                    cv2_img = cv2.inRange(cv2.cvtColor(cv2_img.copy(), cv2.COLOR_BGR2HSV), green_min, green_max)
                    cv2_img = cv2.cvtColor(cv2_img, cv2.COLOR_GRAY2BGR)

                elif calibration_color.value == "z-r":
                    cv2_img = cv2.inRange(cv2.cvtColor(cv2_img, cv2.COLOR_BGR2HSV), red_min_1, red_max_1) + cv2.inRange(cv2.cvtColor(cv2_img, cv2.COLOR_BGR2HSV), red_min_2, red_max_2)
                    cv2_img = cv2.cvtColor(cv2_img, cv2.COLOR_GRAY2BGR)

            counter += 1
            if time.perf_counter() - fps_time > 1:
                fps = int(counter / (time.perf_counter() - fps_time))
                fps_time = time.perf_counter()
                counter = 0

            cv2.putText(cv2_img, str(fps), text_pos, cv2.FONT_HERSHEY_DUPLEX, .7, (0, 255, 0), 1, cv2.LINE_AA)
            cv2.putText(cv2_img, str(zone_similarity_average.value), np.array([int(camera_width * 0.46), int(camera_height * 0.43)]), cv2.FONT_HERSHEY_DUPLEX, .7, (0, 0, 0), 1, cv2.LINE_AA)

            # checking the shared memory buffer size of the image
            # print(image.size)

            buf = np.ndarray(cv2_img.shape, dtype=cv2_img.dtype, buffer=shm_cam2.buf)
            buf[:] = cv2_img[:]

    shm_cam2.close()
    shm_cam2.unlink()
