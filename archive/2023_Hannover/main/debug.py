from sensor_serial import *

screen_x = 1020
screen_y = 540


def get_sensor(num):
    if num == 1 and not sensor_one.value == -1:
        return round(sensor_one.value + (.03 * sensor_one.value + 15.6), 2)
    elif num == 2 and not sensor_two.value == -1:
        return round(sensor_two.value + (.02 * sensor_two.value + 23), 2)
    elif num == 3 and not sensor_three.value == -1:
        return round(sensor_three.value + (-.0025 * sensor_three.value + 30), 2)
    else:
        return -1


if __name__ == "__main__":
    processes = []
    processes.append(multiprocessing.Process(target=serial_loop, args=()))

    for process in processes:
        process.start()
        print(process)
        time.sleep(0.5)

    # fps counter
    fps_time = time.perf_counter()
    counter = 0
    fps = 0

    while True:
        time.sleep(.1)

        gui_img = np.zeros([screen_y, screen_x, 3], dtype=np.uint8)
        gui_img.fill(255)
        gui_img_name = "gui"
        cv2.namedWindow(gui_img_name)
        cv2.moveWindow(gui_img_name, 0, 0)

        # cv2.putText(gui_img, f"{np.mean(sensor1)} mm", (0, int(screen_y * 0.1)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
        cv2.putText(gui_img, f"{get_sensor(1)} mm", (0, int(screen_y * 0.1)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
        cv2.putText(gui_img, "sensor 1", (0, int(screen_y * 0.15)), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        cv2.putText(gui_img, f"{get_sensor(2)} mm", (0, int(screen_y * 0.3)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
        cv2.putText(gui_img, "sensor 2", (0, int(screen_y * 0.35)), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        cv2.putText(gui_img, f"{get_sensor(3)} mm", (0, int(screen_y * 0.5)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
        cv2.putText(gui_img, "sensor 3", (0, int(screen_y * 0.55)), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        cv2.putText(gui_img, f"{sensor_x.value}", (0, int(screen_y * 0.7)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
        cv2.putText(gui_img, "sensor x", (0, int(screen_y * 0.75)), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        cv2.putText(gui_img, f"{sensor_y.value}", (0, int(screen_y * 0.9)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
        cv2.putText(gui_img, "sensor y", (0, int(screen_y * 0.95)), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

        # fps counter 
        counter += 1
        if (time.perf_counter() - fps_time > 1):
            fps = int(counter / (time.perf_counter() - fps_time))
            fps_time = time.perf_counter()
            counter = 0
        cv2.putText(gui_img, str(fps), (int(screen_x * 0.92), int(screen_y * 0.05)), cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 255, 0), 1)

        cv2.imshow(gui_img_name, gui_img)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break

    for process in processes:
        process.terminate()
