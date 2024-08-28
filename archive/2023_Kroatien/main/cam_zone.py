from sensor_serial import *

manager = multiprocessing.Manager()

zone_green_cam_2 = manager.Value("i", False)
zone_red_cam_2 = manager.Value("i", False)
zone_ball_detected_cam_2 = manager.Value("i", False)


def cam_zone_loop():
    # camera setup
    camera_x = 320
    camera_y = 240
    camera = cv2.VideoCapture(1)
    camera.set(3, camera_x)
    camera.set(4, camera_y)
    camera.set(cv2.CAP_PROP_CONTRAST, 11)

    black_min = np.array([0, 0, 0])
    black_max = np.array([100, 100, 100])

    green_min = np.array([45, 65, 60])
    green_max = np.array([180, 255, 255])

    red_min_1 = np.array([0, 100, 90])
    red_max_1 = np.array([10, 255, 255])
    red_min_2 = np.array([170, 100, 100])
    red_max_2 = np.array([180, 255, 255])

    # kernal for the noise reduction
    kernal = np.ones((3, 3), np.uint8)

    # fps counter
    fps_time = time.perf_counter()
    counter = 0
    fps = 0

    circle_last = (camera_x / 2, camera_y / 2)

    _, image = camera.read()
    if image is None:
        print("camera error")
        terminate.value = True
    else:
        print("camera working")

    while not terminate.value:  # switch.value == 1 and
        time.sleep(1)

        while objective.value == "zone" and not terminate.value:
            img_name = "zone_image"
            cv2.namedWindow(img_name)
            cv2.moveWindow(img_name, int((1020 - camera_x) / 2), int((540 - camera_y) / 2))

            _, image = camera.read()

            cv2.rectangle(image, (0, 0), (camera_x, int(camera_y * .35)), (255, 255, 255), -1)

            hsvImage = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

            greenImage = cv2.inRange(hsvImage, green_min, green_max)
            greenImage = cv2.dilate(greenImage, kernal, iterations=2)

            redImage = cv2.inRange(hsvImage, red_min_1, red_max_1) + cv2.inRange(hsvImage, red_min_2, red_max_2)

            blackImage = cv2.inRange(image, black_min, black_max) - greenImage - redImage
            blackImage[blackImage < 2] = 0

            greyImg = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            greyImg = cv2.GaussianBlur(greyImg, (5, 5), 0)

            # detecting balls
            circles = cv2.HoughCircles(greyImg, cv2.HOUGH_GRADIENT, dp=1, minDist=50, param1=50, param2=30, minRadius=5, maxRadius=90)

            if circles is not None and not zone_ball_detected_cam_1.value and not zone_status.value == "pickup_ball" and not (sensor_three.value > 800 or sensor_three.value == -1):
                zone_ball_detected_cam_2.value = True

                circle_candidates = np.array([[camera_x * 2, camera_y * 2, camera_x * 2, camera_x * 5, False]])

                circles = np.round(circles[0, :]).astype("int")
                for (x, y, r) in circles:
                    distance = abs(x - circle_last[0]) + abs(y - circle_last[1])
                    alive = True

                    roi = blackImage[int(max(y - r, 0)): int(min(y + r, camera_y)), int(max(x - r, 0)): int(min(x + r, camera_x))]
                    if np.mean(roi) > 150:
                        distance = distance + camera_x
                        alive = False

                    circle_candidates = np.append(circle_candidates, [[x, y, r, distance, alive]], axis=0)

                circle_candidates = circle_candidates[circle_candidates[:, 3].argsort()].astype("int")

                x, y, r, alive = circle_candidates[0, 0], circle_candidates[0, 1], circle_candidates[0, 2], bool(circle_candidates[0, 4])
                circle_last = (x, y)

                target_offset_x.value = x - camera_x // 2
                target_offset_y.value = -(65 - r)

                cv2.circle(image, (x, y), r, (0, 255, 0), 2)
                cv2.putText(image, f"({target_offset_x.value}, {target_offset_y.value}, {alive})", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

                for (x, y, r) in circles:
                    cv2.circle(blackImage, (x, y), int(r * 1.1), (0, 0, 0), -1)
                    cv2.circle(greenImage, (x, y), int(r * 1.1), (0, 0, 0), -1)
                    cv2.circle(redImage, (x, y), int(r * 1.1), (0, 0, 0), -1)

            else:
                zone_ball_detected_cam_2.value = False

            contours_grn, _ = cv2.findContours(greenImage, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
            contours_red, _ = cv2.findContours(redImage, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

            # detecting green
            found_green = False
            if len(contours_grn) > 0:
                for i in range(len(contours_grn)):
                    if cv2.contourArea(contours_grn[i]) > 20000:
                        found_green = True
                        image = cv2.drawContours(image, [np.int0(cv2.boxPoints(cv2.minAreaRect(contours_grn[i])))], -1, (255, 0, 0), 2)
            if found_green:
                zone_green_cam_2.value = True
            else:
                zone_green_cam_2.value = False

            # detecting red
            found_red = False
            if len(contours_red) > 0:
                for i in range(len(contours_red)):
                    if cv2.contourArea(contours_red[i]) > 20000:
                        found_red = True
                        image = cv2.drawContours(image, [np.int0(cv2.boxPoints(cv2.minAreaRect(contours_red[i])))], -1, (0, 255, 0), 2)
            if found_red:
                zone_red_cam_2.value = True
            else:
                zone_red_cam_2.value = False

            # fps counter 
            counter += 1
            if (time.perf_counter() - fps_time > 1):
                fps = int(counter / (time.perf_counter() - fps_time))
                fps_time = time.perf_counter()
                counter = 0
            cv2.putText(image, str(fps), (int(camera_x * 0.92), int(camera_y * 0.05)), cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 255, 0), 1)

            cv2.imshow(img_name, image)

            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                terminate.value = True
                break

# cam_zone_loop()
