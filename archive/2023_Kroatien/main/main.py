from cam_zone import *
from gpio_controller import *
from gui import *

obstacle_dir = ["l"]
obstacle_count = 0
run = False

last_turn_dir = "l"
last_gyro_y = np.zeros([13])
last_angles = np.zeros([13])

zone_done = False

global got_box
global got_ball
global ball_alive
got_box = False
got_ball = False
ball_alive = True
zone_turn_offset = -3
zone_exit_min_dis = 250
max_balls = 3
max_exit_time = 480

global timer_arr
timer_arr = np.array([["none", 1, 0, 0]])


def set_timer(name, set_time):
    global timer_arr
    timer_arr = np.append(timer_arr, [[name, round(float(time.perf_counter()), 3), 0.0, float(set_time)]], axis=0)


def remove_timer(name):
    global timer_arr
    timer_arr = timer_arr[np.where(timer_arr[:, 0] != name)]


def get_timer(name):
    global timer_arr
    update_timer()
    return np.array([float(timer_arr[np.where(timer_arr[:, 0] == name), 2]), float(timer_arr[np.where(timer_arr[:, 0] == name), 3])])


def update_timer():
    global timer_arr
    for i in range(len(timer_arr)):
        if not timer_arr[i, 0] == "none":
            timer_arr[i, 2] = round(float(time.perf_counter()) - float(timer_arr[i, 1]), 3)


def run_code():
    if switch.value == 1 and not terminate.value:
        return True
    else:
        return False


def round_angle(angle, dir=0, rounding_value=90):
    angle = angle + dir % 360
    return round(angle / rounding_value) * rounding_value % 360


def turn_to(angle, stop_on_black=False, tolerance=1.5, dir="n"):
    print("turn_to: " + str(angle))
    speed = 0

    if dir == "r":
        steer(180, 50)
        time.sleep(.3)
        steer()
    elif dir == "l":
        steer(-180, 50)
        time.sleep(.3)
        steer()

    if stop_on_black:
        while not angle - tolerance < sensor_x.value < angle + tolerance and not line_detected.value and not zone_ball_detected_cam_1.value and not zone_ball_detected_cam_2.value and run_code():
            if abs(x_acc_mean.value) < .4 and abs((((angle - sensor_x.value) + 180) % 360) - 180) > 5 and not speed == 15:
                speed = 15
            elif (abs(x_acc_mean.value) > .7 or abs((((angle - sensor_x.value) + 180) % 360) - 180) < 5) and speed == 15:
                speed = 0

            if ((angle - sensor_x.value + 540) % 360 - 180) < 0:
                steer(-180, (abs((angle - sensor_x.value + 540) % 360 - 180) / 180 * 48) + 28 + speed)
            else:
                steer(180, (abs((angle - sensor_x.value + 540) % 360 - 180) / 180 * 48) + 28 + speed)

    else:
        while not angle - tolerance < sensor_x.value < angle + tolerance and run_code():
            if abs(x_acc_mean.value) < .4 and abs((((angle - sensor_x.value) + 180) % 360) - 180) > 5 and not speed == 15:
                speed = 15
            elif (abs(x_acc_mean.value) > .7 or abs((((angle - sensor_x.value) + 180) % 360) - 180) < 5) and speed == 15:
                speed = 0

            if ((angle - sensor_x.value + 540) % 360 - 180) < 0:
                steer(-180, (abs((angle - sensor_x.value + 540) % 360 - 180) / 180 * 48) + 28 + speed)
            else:
                steer(180, (abs((angle - sensor_x.value + 540) % 360 - 180) / 180 * 48) + 28 + speed)
    steer()


def turn_by(angle, tolerance=.5):
    turn_to_angle = (sensor_x.value + angle) % 360

    while not turn_to_angle - tolerance < sensor_x.value < turn_to_angle + tolerance and run_code():
        if ((turn_to_angle - sensor_x.value + 540) % 360 - 180) < 0:
            steer(-180, (abs((angle - sensor_x.value + 540) % 360 - 180) / 180 * 48) + 24)
        else:
            steer(180, (abs((angle - sensor_x.value + 540) % 360 - 180) / 180 * 48) + 24)
    steer()


def turn_to_target(tolerance=7, speed=1, ball_cam_2=False):
    last_offset_x = target_offset_x.value
    last_offset_y = target_offset_y.value

    while not (tolerance > target_offset_x.value > -tolerance and tolerance > target_offset_y.value > -tolerance) and (box_detected.value or zone_ball_detected_cam_1.value or zone_ball_detected_cam_2.value) and run_code():
        while not tolerance * .7 > target_offset_x.value > -(tolerance * .7) and (box_detected.value or zone_ball_detected_cam_1.value or zone_ball_detected_cam_2.value) and target_offset_y.value < (last_offset_y + 10) * 1.2 and run_code():
            if ball_cam_2:
                if zone_ball_detected_cam_1.value:
                    return
                tolerance, speed = update_tolerance()
            if target_offset_x.value > 0:
                steer(180, int((24 * (target_offset_x.value / 180) + 26) * speed))
            else:
                steer(-180, int((24 * (abs(target_offset_x.value) / 180) + 25) * speed))
        last_offset_x = target_offset_x.value

        while not tolerance * .7 > target_offset_y.value > -(tolerance * .7) and (box_detected.value or zone_ball_detected_cam_1.value or zone_ball_detected_cam_2.value) and target_offset_x.value < (last_offset_x + 10) * 1.2 and run_code():
            if ball_cam_2:
                if zone_ball_detected_cam_1.value:
                    return
                tolerance, speed = update_tolerance()
            if target_offset_y.value > 0:
                steer(200, int(18 * speed))
            else:
                steer(0, int(18 * speed))
        last_offset_y = target_offset_y.value
    steer()


def update_tolerance():
    return max(7 - ((target_offset_y.value / 65) * 15), 7), max(.8 - ((target_offset_y.value / 65) * .6), .8)


def pick_up_object(is_wall=False):
    if box_detected.value or zone_ball_detected_cam_1.value:
        if is_wall:
            steer(200, 55)
            time.sleep(.75)
            steer()

            armpos(4)
            time.sleep(1.5)

            steer(0, 50)
            time.sleep(.4)
            steer()

            time.sleep(5.5)

            steer(200, 55)
            time.sleep(.3)
            steer()

            armpos(1)
            time.sleep(3)

            steer(0, 55)
            time.sleep(.40)
            steer()
        else:
            steer(200, 55)
            time.sleep(.46)  # .45
            steer()

            armpos(4)
            time.sleep(7)
            armpos(1)
            time.sleep(3)

            steer(0, 55)
            time.sleep(.40)
            steer()


def drive_until_wall(check_corners=False, check_exit=False, timer_name="n", start_on_exit=True, check_balls=False, speed=60):
    is_timer = True
    if (sensor_five.value > zone_exit_min_dis or sensor_five.value == -1) and start_on_exit:
        start_on_exit = True
    else:
        start_on_exit = False

    while run_code():
        steer(0, speed)
        if start_on_exit and -1 < sensor_five.value < 100:
            start_on_exit = False

        if not timer_name == "n":
            if get_timer(timer_name)[0] > get_timer(timer_name)[1]:
                is_timer = False

        if -1 < sensor_three.value < 80:
            print("wall")
            return "wall"
        elif zone_green_cam_2.value and -1 < sensor_one.value < 110:
            if check_corners:
                zone_green_corner_angle.value = round_angle(sensor_x.value, -45, 45)
                turn_corner("green")
            print("corner")
            return "corner"
        elif zone_red_cam_2.value and -1 < sensor_one.value < 110:
            if check_corners:
                zone_red_corner_angle.value = round_angle(sensor_x.value, -45, 45)
                turn_corner("red")
            print("corner")
            return "corner"
        elif zone_white_cam_1.value and (sensor_three.value > zone_exit_min_dis or sensor_three.value == -1) and (sensor_one.value > zone_exit_min_dis or sensor_one.value == -1):
            steer(200, 60)
            time.sleep(.5)
            print("entrance")
            return "entrance"
        elif zone_black_cam_1.value and (sensor_three.value > zone_exit_min_dis or sensor_three.value == -1) and (sensor_two.value > zone_exit_min_dis or sensor_two.value == -1) and (sensor_one.value > zone_exit_min_dis or sensor_one.value == -1) and not zone_green_cam_2.value and not zone_white_cam_1.value:
            steer(200, 60)
            time.sleep(.5)
            if check_exit:
                zone_exit_angle.value = round_angle(sensor_x.value)
            print("exit")
            return "exit"
        elif (sensor_five.value > zone_exit_min_dis or sensor_five.value == -1) and check_exit and not start_on_exit:
            if zone_exit_angle.value == -1 or zone_status.value == "find_exit":
                steer(0, 50)
                time.sleep(.2)

                turn_to(round_angle(sensor_x.value, -90))

                if sensor_three.value > zone_exit_min_dis or sensor_three.value == -1:
                    set_timer("zone_exit_forward", 1.8)

                    if zone_white_cam_1.value:
                        found_white = True
                    else:
                        found_white = False

                    if zone_black_cam_1.value:
                        found_black = True
                    else:
                        found_black = False

                    while not zone_white_cam_1.value and not get_timer("zone_exit_forward")[0] > get_timer("zone_exit_forward")[1] and run_code():
                        if zone_black_cam_1.value:
                            found_black = True
                        if zone_white_cam_1.value:
                            found_white = True
                        steer(0, 40)
                    steer()

                    if found_black and not found_white:
                        zone_exit_angle.value = round_angle(sensor_x.value)
                        steer(200, 40)
                        time.sleep(get_timer("zone_exit_forward")[0] + .4)
                        print("exit")
                        remove_timer("zone_exit_forward")
                        return "exit"
                    elif found_white:
                        steer(200, 40)
                        time.sleep(get_timer("zone_exit_forward")[0] + .4)
                        print("entrance")
                        remove_timer("zone_exit_forward")
                        return "entrance"
                    else:
                        print("none")
                        remove_timer("zone_exit_forward")
                        return "none"
        elif not is_timer:
            print("timer")
            return "timer"
        elif (zone_ball_detected_cam_1.value or zone_ball_detected_cam_2.value) and check_balls:
            print("ball")
            return "ball"


def turn_corner(color):
    global got_box
    global got_ball
    global ball_alive

    turn_to(round_angle(sensor_x.value, 45, 45))
    steer(0, 60)
    time.sleep(.55)
    steer()

    if (color == "green" and (got_box or (got_ball and ball_alive))) or (color == "red" and got_ball and not ball_alive):
        turn_to(round_angle(sensor_x.value, -90, 45))

        if got_box:
            dump_victims(True)
        else:
            dump_victims()

        turn_to(round_angle(sensor_x.value, 90, 45))

    if run_code():
        if got_box and color == "green":
            got_box = False
        elif got_ball and ball_alive and color == "green":
            zone_ball_alive_counter.value = zone_ball_alive_counter.value + 1
            got_ball = False
        elif got_ball and not ball_alive and color == "red":
            zone_ball_dead_counter.value = zone_ball_dead_counter.value + 1
            got_ball = False

        if (zone_ball_alive_counter.value >= 2 and zone_ball_dead_counter.value >= 1) or zone_ball_alive_counter.value + zone_ball_dead_counter.value >= max_balls or run_time.value > max_exit_time and not got_ball:
            zone_status.value = "find_exit"

        if zone_green_corner_angle.value == -1 or zone_red_corner_angle.value == -1 or zone_status.value == "find_exit" or (zone_status.value == "return_corner" and got_ball):
            steer(0, 50)
            time.sleep(1.2)
            turn_to((round_angle(sensor_x.value, 45) + zone_turn_offset) % 360)
        else:
            zone_status.value = "find_ball_1"


def dump_victims(rescue_kit=False):
    steer(200, 55)
    time.sleep(.25)
    steer()

    if rescue_kit:
        armpos(5)
        time.sleep(7)

    armpos(3)
    time.sleep(2.5)

    steer(200, 90)
    time.sleep(.25)
    steer(0, 90)
    time.sleep(.15)

    steer()
    time.sleep(.5)

    steer(200, 90)
    time.sleep(.25)
    steer(0, 90)
    time.sleep(.15)

    steer()
    time.sleep(.5)

    while sensor_four.value < 10 and run_code():
        steer(200, 90)
        time.sleep(.25)
        steer(0, 90)
        time.sleep(.15)

        steer()
        time.sleep(.5)

    time.sleep(1)
    armpos(1)
    time.sleep(2)
    steer(0, 45)
    time.sleep(.5)


if __name__ == "__main__":
    processes = []
    processes.append(multiprocessing.Process(target=serial_loop, args=()))
    processes.append(multiprocessing.Process(target=sysinfo_loop, args=()))
    processes.append(multiprocessing.Process(target=cam_loop, args=()))
    processes.append(multiprocessing.Process(target=gui_loop, args=[.5]))
    processes.append(multiprocessing.Process(target=cam_zone_loop, args=()))

    for process in processes:
        process.start()
        print(process)
        time.sleep(0.5)

    while not terminate.value:
        # reset
        if not run and switch.value == 1 and not objective.value == "test":
            armpos(1)
            gyro_x_offset(0)
            gyro_y_offset(0)
            last_gyro_y = np.zeros([13])
            last_angles = np.zeros([13])
            timer_arr = timer_arr[np.where(timer_arr[:, 0] == "none")]
            white_mean.value = 0
            objective.value = "follow_line"  # follow_line zone
            line_status.value = "line_detected"
            zone_status.value = "begin"  # begin find_ball
            zone_green_corner_angle.value = -1
            zone_red_corner_angle.value = -1

            if start_time.value == -1:
                start_time.value = time.perf_counter()

        # run if switch is true
        if switch.value == 1:
            run = True
        else:
            run = False

        # read gyro_y
        if sensor_y.value > 10:
            rotation_y.value = "ramp_up"
        elif sensor_y.value < -6.5:
            rotation_y.value = "ramp_down"
        else:
            rotation_y.value = "none"

        if run:
            # test
            if objective.value == "test":
                while run_code():
                    steer(180, 28)
                    pass

            if objective.value == "follow_line":

                if line_detected.value:
                    line_status.value = "line_detected"
                    min_line_size.value = 5000
                elif not line_detected.value and not line_status.value == "obstacle_avoid" and not line_status.value == "gap_avoid":
                    line_status.value = "gap_detected"
                    steer()

                # stop on red
                if red_detected.value:
                    objective.value = "stop"
                    steer()
                    time.sleep(9)

                    if run_code():
                        steer(0, 55)
                        time.sleep(.5)
                        steer()

                    objective.value = "follow_line"

                # seesaw
                if np.mean(last_gyro_y) > 13 and sensor_y.value < -13:
                    steer()
                    time.sleep(2)
                    steer(200, 55)
                    time.sleep(1)
                    last_gyro_y = np.zeros([13])
                last_gyro_y = np.delete(np.append(last_gyro_y, sensor_y.value), 0)

                # switch to zone
                if white_mean.value > 10 and -5 < np.mean(last_gyro_y) < 5 and not zone_done:
                    objective.value = "zone"
                    time.sleep(.2)
                    line_detected.value = False

                if line_status.value == "line_detected":

                    # switch to pick-up_box
                    if box_detected.value and rotation_y.value == "none" and line_status.value == "line_detected":
                        objective.value = "pick-up_box"

                    # turn around
                    if turn_dir.value == "turn_around":
                        steer(0)
                        time.sleep(.5)
                        steer()
                        turn_to(round_angle(sensor_x.value, 180), False, 1.5, last_turn_dir)
                        if last_turn_dir == "l":
                            last_turn_dir = "r"
                        else:
                            last_turn_dir = "l"

                    # obstacle
                    if -1 < sensor_one.value <= 90 and -1 < sensor_two.value <= 90 and -1 < sensor_three.value <= 90 and abs((sensor_one.value + sensor_two.value + sensor_three.value) - (sensor_three.value * 3)) < 45 and rotation_y.value == "none" and -5 < np.mean(last_gyro_y) < 5:
                        line_status.value = "obstacle_detected"
                        steer(200, 60)
                        time.sleep(.4)
                        if obstacle_dir[obstacle_count % len(obstacle_dir)] == "l":
                            obstacle_direction.value = "l"

                            if np.mean(last_angles) > 60:
                                turn_to(round_angle(sensor_x.value, -20, 45))  # -20 vorher -70
                            elif np.mean(last_angles) < -60:
                                turn_to(round_angle(sensor_x.value, -70, 45))
                            else:
                                turn_to(round_angle(sensor_x.value, -45, 45))

                            steer(0, 50)
                            time.sleep(1)
                            steer(150, 55)
                            time.sleep(1)

                        elif obstacle_dir[obstacle_count % len(obstacle_dir)] == "r":
                            obstacle_direction.value = "r"

                            if np.mean(last_angles) > 60:
                                turn_to(round_angle(sensor_x.value, 70, 45))
                            elif np.mean(last_angles) < -60:
                                turn_to(round_angle(sensor_x.value, 20, 45))  # +20 vorher 70
                            else:
                                turn_to(round_angle(sensor_x.value, 45, 45))

                            steer(0, 50)
                            time.sleep(.9)
                            steer(-150, 55)
                            time.sleep(1)

                        min_line_size.value = 6000
                        line_status.value = "obstacle_avoid"

                        while not line_detected.value and run_code():
                            if obstacle_dir[obstacle_count % len(obstacle_dir)] == "l":
                                steer(150, 55)
                            elif obstacle_dir[obstacle_count % len(obstacle_dir)] == "r":
                                steer(-150, 55)

                        obstacle_count = obstacle_count + 1

                    if rotation_y.value == "ramp_up":
                        if abs(line_angle.value < 100):
                            steer(line_angle.value, 65)
                        else:
                            steer(line_angle.value, 70)

                    elif rotation_y.value == "ramp_down":
                        if abs(line_angle.value) > 150:
                            steer(line_angle.value, 45)
                        else:
                            steer(line_angle.value, 25)
                    elif rotation_y.value == "none":
                        steer(line_angle.value, 60)

                    # save last angles
                    last_angles = np.delete(np.append(last_angles, line_angle.value), 0)

                elif line_status.value == "gap_detected":
                    steer()
                    time.sleep(.5)
                    min_line_size.value = 6000
                    print(last_angles)
                    print(np.mean(last_angles))
                    if np.mean(last_angles) > 30:
                        turn_to(round_angle(sensor_x.value, 30), True, 2)
                    elif np.mean(last_angles) < -30:
                        turn_to(round_angle(sensor_x.value, -30), True, 2)
                    else:
                        turn_to(round_angle(sensor_x.value), True, 2)
                    line_status.value = "gap_avoid"

                elif line_status.value == "gap_avoid":
                    steer(0, 45)

            # box
            elif objective.value == "pick-up_box":
                steer()
                time.sleep(1)

                if not box_detected.value:
                    steer(200, 55)
                    time.sleep(.2)

                boxPos_x = target_offset_x.value
                boxPos_y = target_offset_y.value

                turn_to_target()
                pick_up_object()

                while not line_detected.value and not box_detected.value and run_code():
                    if boxPos_x > 0:
                        steer(-180, 40)
                    else:
                        steer(180, 40)

                if not box_detected.value:
                    got_box = True
                    objective.value = "follow_line"

            elif objective.value == "zone":

                if zone_status.value == "begin":
                    steer()
                    time.sleep(1)

                    if np.mean(last_angles[:(len(last_angles) - 3)]) > 30:
                        turn_to(round_angle(sensor_x.value, 25), False, .7)
                    elif np.mean(last_angles[:(len(last_angles) - 3)]) < -30:
                        turn_to(round_angle(sensor_x.value, -25), False, .7)
                    else:
                        turn_to(round_angle(sensor_x.value), False, .7)

                    gyro_x_offset(0)
                    gyro_y_offset(0)

                    steer(0, 55)
                    time.sleep(.5)

                    turn_to(7)

                    steer(0, 55)
                    time.sleep(.8)

                    if zone_red_corner_angle.value == -1 or zone_green_corner_angle.value == -1 and not run_time.value > max_exit_time:
                        turn_to((270 + zone_turn_offset) % 360)
                        zone_status.value = "check_corners"
                    elif (zone_ball_alive_counter.value >= 2 and zone_ball_dead_counter.value >= 1) or zone_ball_alive_counter.value + zone_ball_dead_counter.value >= max_balls or run_time.value > max_exit_time:
                        zone_status.value = "find_exit"
                    else:
                        if not (zone_ball_detected_cam_1.value or zone_ball_detected_cam_2.value):
                            set_timer("find_ball_2_forward", 2.5)

                            drive_until_wall(False, False, "find_ball_2_forward", True, True, 40)

                            remove_timer("find_ball_2_forward")

                        zone_status.value = "find_ball"

                elif zone_status.value == "check_corners":
                    while zone_status.value == "check_corners" and run_code():
                        if not drive_until_wall(True, True) == "corner":
                            turn_to((round_angle(sensor_x.value, 90) + zone_turn_offset) % 360)

                elif zone_status.value == "find_ball_1":
                    turn_to(((sensor_x.value + 90) % 360), True)

                    if not (zone_ball_detected_cam_1.value or zone_ball_detected_cam_2.value):
                        set_timer("find_ball_1_forward", 2.5)

                        drive_until_wall(False, False, "find_ball_1_forward", True, True, 40)

                        remove_timer("find_ball_1_forward")

                    zone_status.value = "find_ball"

                elif zone_status.value == "find_ball_2":
                    turn_to(round_angle(sensor_x.value, 45), True)

                    if not (zone_ball_detected_cam_1.value or zone_ball_detected_cam_2.value):
                        set_timer("find_ball_2_forward", 2.5)

                        drive_until_wall(False, False, "find_ball_2_forward", True, True, 40)

                        remove_timer("find_ball_2_forward")

                    zone_status.value = "find_ball"

                elif zone_status.value == "find_ball":
                    if zone_ball_detected_cam_1.value:
                        zone_status.value = "pickup_ball"
                    elif zone_ball_detected_cam_2.value and not zone_ball_detected_cam_1.value:
                        if abs(target_offset_y.value) > 25:
                            steer(0, 50)
                        else:
                            steer()

                        time.sleep(.3)
                        turn_to_target(7, .9, True)

                        if zone_ball_detected_cam_2.value and -10 < target_offset_x.value < 10 and -10 < target_offset_y.value < 10:
                            set_timer("zone_ball_forward", 3)
                            while not zone_ball_detected_cam_1.value and get_timer("zone_ball_forward")[0] < get_timer("zone_ball_forward")[1] and run_code():
                                steer(0, 15)
                            remove_timer("zone_ball_forward")

                            if zone_ball_detected_cam_1.value:
                                zone_status.value = "pickup_ball"
                            else:
                                steer(200, 40)
                                time.sleep(1)

                    else:
                        set_timer("find_ball_spin", 13)
                        while not (zone_ball_detected_cam_2.value or zone_ball_detected_cam_1.value) and get_timer("find_ball_spin")[0] < get_timer("find_ball_spin")[1] and run_code():
                            steer(180, 40)
                        steer()
                        if get_timer("find_ball_spin")[0] >= get_timer("find_ball_spin")[1]:
                            zone_status.value = "find_ball_2"
                        remove_timer("find_ball_spin")

                elif zone_status.value == "pickup_ball":
                    steer()

                    if zone_ball_detected_cam_1.value and zone_ball_alive.value or (not zone_ball_alive.value and zone_ball_alive_counter.value >= 2):
                        turn_to_target(20, .7)

                        if zone_ball_detected_cam_1.value:
                            ball_alive = zone_ball_alive.value
                            if sensor_three.value < 200:
                                pick_up_object(True)
                            else:
                                pick_up_object()

                        if sensor_four.value < 15:
                            zone_status.value = "return_corner"
                            got_ball = True
                        else:
                            zone_status.value = "find_ball"

                    elif not zone_white_cam_1.value:
                        turn_to((sensor_x.value + 30) % 360)
                        turn_to((sensor_x.value + 80) % 360, True)
                        set_timer("dead_victim", 1.5)
                        drive_until_wall(False, False, "dead_victim", True, True, 40)
                        remove_timer("dead_victim")
                        zone_status.value = "find_ball"

                elif zone_status.value == "return_corner":
                    if ball_alive:
                        turn_to(round_angle(zone_green_corner_angle.value, -135))
                    else:
                        turn_to(round_angle(zone_red_corner_angle.value, -135))

                    set_timer("return_corner_forward", 1.5)

                    drive_until_wall(False, False, "return_corner_forward")

                    remove_timer("return_corner_forward")

                    if ball_alive:
                        turn_to(round_angle(zone_green_corner_angle.value, -45))
                    else:
                        turn_to(round_angle(zone_red_corner_angle.value, -45))

                    if not drive_until_wall(True) == "corner":
                        if ball_alive:
                            turn_to((round_angle(zone_green_corner_angle.value, 45) + zone_turn_offset) % 360)
                        else:
                            turn_to((round_angle(zone_red_corner_angle.value, 45) + zone_turn_offset) % 360)

                    drive_until_wall(True)

                elif zone_status.value == "find_exit":
                    if not zone_exit_angle.value == -1:
                        break_reason = "n"
                        if not zone_exit_angle.value == round_angle(sensor_x.value, -90):
                            turn_to(round_angle(zone_exit_angle.value, -90))

                            if not drive_until_wall(True) == "corner":
                                turn_to((round_angle(sensor_x.value, 90) + zone_turn_offset) % 360)

                            break_reason = drive_until_wall(True)
                            if not break_reason == "corner" and not break_reason == "exit":
                                turn_to((round_angle(sensor_x.value, 90) + zone_turn_offset) % 360)

                        if not break_reason == "exit":
                            if drive_until_wall(False, True, "n", False) == "entrance":
                                turn_to((round_angle(sensor_x.value, 90) + zone_turn_offset) % 360)
                                steer(0, 60)
                                time.sleep(1)
                                drive_until_wall(False, True)

                    while zone_exit_angle.value == -1 and run_code():
                        break_reason = drive_until_wall(True, True)
                        if not break_reason == "corner" and not break_reason == "exit":
                            turn_to((round_angle(sensor_x.value, 90) + zone_turn_offset) % 360)

                    if (sensor_three.value > zone_exit_min_dis or sensor_three.value == -1) and (sensor_two.value > zone_exit_min_dis or sensor_two.value == -1) and (sensor_one.value > zone_exit_min_dis or sensor_one.value == -1) and run_code():
                        steer(0, 50)
                        time.sleep(.8)
                        objective.value = "follow_line"
                        zone_status.value = "none"
                        zone_done = True
                    else:
                        turn_to(round_angle(sensor_x.value, 180))
        else:
            steer()

        time.sleep(.1)

    for process in processes:
        process.terminate()
    GPIO_reset()
