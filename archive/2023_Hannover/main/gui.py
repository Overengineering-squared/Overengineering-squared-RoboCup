# from ctypes import cdll
# from os import getuid

from main import *

screen_x = 1020
screen_y = 540

manager = multiprocessing.Manager()


def gui_loop(wait_time):
    while True:
        gui_img = np.zeros([screen_y, screen_x, 3], dtype=np.uint8)
        gui_img.fill(255)
        gui_img_name = "gui"
        cv2.namedWindow(gui_img_name)
        cv2.moveWindow(gui_img_name, 0, 0)

        cv2.putText(gui_img, f"{sensor_one.value} mm", (0, int(screen_y * 0.1)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
        cv2.putText(gui_img, "sensor 1", (0, int(screen_y * 0.15)), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        cv2.putText(gui_img, f"{sensor_two.value} mm", (0, int(screen_y * 0.3)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
        cv2.putText(gui_img, "sensor 2", (0, int(screen_y * 0.35)), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        cv2.putText(gui_img, f"{sensor_three.value} mm", (0, int(screen_y * 0.5)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
        cv2.putText(gui_img, "sensor 3", (0, int(screen_y * 0.55)), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        cv2.putText(gui_img, f"{sensor_x.value}", (0, int(screen_y * 0.7)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
        cv2.putText(gui_img, "sensor x", (0, int(screen_y * 0.75)), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        cv2.putText(gui_img, f"{sensor_y.value}", (0, int(screen_y * 0.9)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
        cv2.putText(gui_img, "sensor y", (0, int(screen_y * 0.95)), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

        cv2.putText(gui_img, f"{str(switch.value)}", (int(screen_x * 0.8), int(screen_y * 0.3)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
        cv2.putText(gui_img, "switch", (int(screen_x * 0.8), int(screen_y * 0.35)), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        cv2.putText(gui_img, f"{str(turn_dir.value)}", (int(screen_x * 0.8), int(screen_y * 0.5)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
        cv2.putText(gui_img, "turn_dir", (int(screen_x * 0.8), int(screen_y * 0.55)), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        cv2.putText(gui_img, f"{str(line_count.value)}", (int(screen_x * 0.8), int(screen_y * 0.7)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
        cv2.putText(gui_img, "line count", (int(screen_x * 0.8), int(screen_y * 0.75)), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        cv2.putText(gui_img, f"{str(status.value)}", (int(screen_x * 0.8), int(screen_y * 0.9)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
        cv2.putText(gui_img, "status", (int(screen_x * 0.8), int(screen_y * 0.95)), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

        if line_angle.value > 0:
            cv2.putText(gui_img, str(line_angle.value), (655, 455), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        elif line_angle.value < 0:
            cv2.putText(gui_img, str(line_angle.value), (336, 455), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        elif line_angle.value == 0:
            cv2.putText(gui_img, str(line_angle.value), (510, 455), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

        cpu_color = (205, 0, 0)
        if cpu.value > 24:
            cpu_color = (0, 255, 0)
        if cpu.value > 49:
            cpu_color = (0, 215, 255)
        if cpu.value > 69:
            cpu_color = (0, 69, 255)
        if cpu.value > 84:
            cpu_color = (0, 0, 139)
        cv2.putText(gui_img, f"{cpu.value}%", (int(screen_x * 0.932), int(screen_y * 0.05)), cv2.FONT_HERSHEY_SIMPLEX, 1, cpu_color, 2)
        cv2.putText(gui_img, "CPU", (int(screen_x * 0.94), int(screen_y * 0.1)), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

        cv2.imshow(gui_img_name, gui_img)

        time.sleep(wait_time)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break
