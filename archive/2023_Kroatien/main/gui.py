from main import *

screen_x = 1020
screen_y = 540


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

        cv2.putText(gui_img, f"{switch.value}", (int(screen_x * 0.75), int(screen_y * 0.1)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
        cv2.putText(gui_img, "switch", (int(screen_x * 0.75), int(screen_y * 0.15)), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        cv2.putText(gui_img, f"{objective.value}", (int(screen_x * 0.75), int(screen_y * 0.3)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
        cv2.putText(gui_img, "objective", (int(screen_x * 0.75), int(screen_y * 0.35)), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

        cv2.putText(gui_img, f"{sensor_ax.value}", (400, 525), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        cv2.putText(gui_img, f"{sensor_ay.value}", (600, 525), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

        cv2.putText(gui_img, str(round(x_acc_mean.value, 2)), (510, 525), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

        cv2.putText(gui_img, f"{run_time.value}", (510, int(screen_y * 0.05)), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

        if objective.value == "zone":
            cv2.putText(gui_img, f"{zone_green_corner_angle.value}", (int(screen_x * 0.75), int(screen_y * 0.5)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(gui_img, f"{zone_red_corner_angle.value}", (int(screen_x * 0.82), int(screen_y * 0.5)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            cv2.putText(gui_img, "corner angles", (int(screen_x * 0.75), int(screen_y * 0.55)), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
            cv2.putText(gui_img, f"{zone_exit_angle.value}", (int(screen_x * 0.75), int(screen_y * 0.7)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
            cv2.putText(gui_img, f"{sensor_five.value} mm", (int(screen_x * 0.82), int(screen_y * 0.7)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
            cv2.putText(gui_img, "exit angle", (int(screen_x * 0.75), int(screen_y * 0.75)), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
            cv2.putText(gui_img, f"{zone_status.value}", (int(screen_x * 0.75), int(screen_y * 0.9)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
            cv2.putText(gui_img, "zone status", (int(screen_x * 0.75), int(screen_y * 0.95)), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
            cv2.putText(gui_img, f"{zone_green_cam_2.value}", (655, 455), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
            cv2.putText(gui_img, f"{zone_black_cam_1.value}", (490, 455), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(gui_img, f"{zone_white_cam_1.value}", (490, 480), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (150, 150, 150), 2)
            cv2.putText(gui_img, f"{zone_red_cam_2.value}", (310, 455), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

            cv2.putText(gui_img, f"{zone_ball_alive_counter.value}", (420, 490), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (150, 150, 150), 2)
            cv2.putText(gui_img, f"{zone_ball_dead_counter.value}", (600, 490), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

            cv2.putText(gui_img, f"{sensor_four.value}", (310, 490), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

        else:
            cv2.putText(gui_img, f"{rotation_y.value}", (int(screen_x * 0.75), int(screen_y * 0.5)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
            cv2.putText(gui_img, "rotation_y", (int(screen_x * 0.75), int(screen_y * 0.55)), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
            cv2.putText(gui_img, f"{turn_dir.value}", (int(screen_x * 0.75), int(screen_y * 0.7)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
            cv2.putText(gui_img, "turn dirction", (int(screen_x * 0.75), int(screen_y * 0.75)), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
            cv2.putText(gui_img, f"{line_status.value}", (int(screen_x * 0.75), int(screen_y * 0.9)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
            cv2.putText(gui_img, "line status", (int(screen_x * 0.75), int(screen_y * 0.95)), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

            if line_angle.value > 0:
                cv2.putText(gui_img, f"{line_angle.value}", (655, 455), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
            elif line_angle.value < 0:
                cv2.putText(gui_img, f"{line_angle.value}", (336, 455), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
            elif line_angle.value == 0:
                cv2.putText(gui_img, f"{line_angle.value}", (510, 455), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

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
            terminate.value = True
            break
