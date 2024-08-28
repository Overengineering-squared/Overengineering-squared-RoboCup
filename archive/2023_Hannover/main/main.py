from gpio_controller import *
from gui import *
from sensor_serial import *

if __name__ == "__main__":
    processes = []
    processes.append(multiprocessing.Process(target=serial_loop, args=()))
    processes.append(multiprocessing.Process(target=sysinfo_loop, args=()))
    processes.append(multiprocessing.Process(target=line_loop, args=()))
    processes.append(multiprocessing.Process(target=gui_loop, args=[.5]))

    for process in processes:
        process.start()
        print(process)
        time.sleep(0.5)

    is_line = True
    obstacle_left = True
    last_gyro_y = 0
    while not terminate.value:
        gyro_x_offset(0)
        gyro_y_offset(0)
        while switch.value == 1 and not terminate.value:
            time.sleep(0.1)
            if not sensor_x.value == 361 and not sensor_y.value == 361:

                if last_gyro_y > 10 and sensor_y.value < -5:
                    steer(200)
                    time.sleep(1)
                    status.value = "line"
                    print("test")

                if turn_dir.value == "turn_around":
                    steer(-180)
                    time.sleep(3.5)

                if status.value == "stop":
                    steer(190)
                    time.sleep(6)
                    status.value = "line"

                if line_count.value > 0:
                    is_line = True
                else:
                    is_line = False

                if is_line and status.value == "obstacle":
                    status.value = "line"

                if -1 < sensor_two.value <= 90 and -1 < sensor_three.value <= 90 and status.value == "line" and abs((sensor_two.value + sensor_three.value) - (sensor_two.value * 2)) < 30:  # -1 < sensor_one.value <= 90 and # sensor_one.value +
                    status.value = "obstacle"
                    steer(200, 60)  # backward
                    time.sleep(0.45)
                    if obstacle_left:
                        steer(-180, 60)
                    else:
                        steer(180, 60)
                    time.sleep(.7)
                    steer(0, 60)
                    time.sleep(.7)
                    if obstacle_left:
                        steer(150, 60)
                    else:
                        steer(-150, 60)
                    time.sleep(0.5)

                if is_line == False and status.value == "line" and (-130 < line_angle.value < 130):
                    status.value = "turning"
                    # turn left
                    if 1 < sensor_x.value <= 45 or 91 < sensor_x.value <= 135 or 181 < sensor_x.value <= 225 or 271 < sensor_x.value <= 315:
                        steer(-180, 35)
                    # turn right
                    elif 315 < sensor_x.value <= 359 or 45 < sensor_x.value <= 89 or 135 < sensor_x.value <= 179 or 225 < sensor_x.value <= 269:
                        steer(180, 35)

                if status.value == "gap" and is_line:
                    status.value = "line"

                if status.value == "turning":
                    if sensor_x.value % 90 >= 80 or sensor_x.value % 90 <= 10:
                        status.value = "gap"

                if sensor_y.value > 9 and status.value == "line":
                    status.value = "ramp_up"
                elif sensor_y.value < -6 and status.value == "line":
                    status.value = "ramp_down"
                elif -6 <= sensor_y.value <= 9 and status.value == "ramp_up" or status.value == "ramp_down":
                    status.value = "line"

                if is_line and status.value == "line":
                    steer(line_angle.value)
                elif is_line and status.value == "ramp_up":
                    if line_angle.value >= 0:
                        steer(min(line_angle.value, 100), 50)
                    else:
                        steer(max(line_angle.value, -100), 50)
                elif is_line and status.value == "ramp_down":
                    steer(line_angle.value, 15)
                elif not is_line and status.value == "gap":
                    steer(0)
                elif not is_line and status.value == "no_line":
                    steer(190)
                elif not is_line and status.value == "obstacle":
                    if obstacle_left:
                        steer(150, 60)
                    else:
                        steer(-150, 60)

                last_gyro_y = sensor_y.value
        while switch.value == 0 and not terminate.value:
            time.sleep(0.1)
            steer(190)

    for process in processes:
        process.terminate()
    GPIO_reset()
