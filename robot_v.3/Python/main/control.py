import random
from math import isclose, pow

from gpiozero import Button, LED, PWMLED

from Managers import Timer
from line_cam import camera_x, camera_y
from mp_manager import *

print_obstacle = False
speed_zone = False

# program variables
wait_time_red = 9

max_turn_angle = 110

last_turn_dir = "l"

obstacle_dir = ["l", "r"]
obstacle_count = 0

obstacle_on_ramp = True
orientate_at_corner = True
turn_around_ramp_side = True

turn_around_45 = False

# average time variables
time_last_angles = empty_time_arr()

time_last_gyro_y = empty_time_arr()
time_last_gyro_x = empty_time_arr()
time_last_gyro_z = empty_time_arr()

time_sensor_one = empty_time_arr()
time_sensor_two = empty_time_arr()
time_sensor_three = empty_time_arr()
time_sensor_four = empty_time_arr()
time_sensor_five = empty_time_arr()
time_sensor_six = empty_time_arr()
time_sensor_seven = empty_time_arr()

time_silver_detected = empty_time_arr()
time_silver_angle = empty_time_arr()
time_exit_angle = empty_time_arr()
time_line_similarity = fill_array(0, 1200)
time_zone_similarity = fill_array(0.7, 1200)

time_victim_type = empty_time_arr(1200)

timer = Timer()

run = True
zone_done = False
dumped_alive_victims = False
dumped_dead_victims = False

# gpio pins
in_1 = 0  # forwards right
in_2 = 1  # backwards right
in_3 = 5  # forwards left
in_4 = 6  # backwards right
en_a = 12  # speed right
en_b = 13  # speed left

servo_control_pin = 7
servo_pin_1 = 8
servo_pin_2 = 23
servo_pin_3 = 24

led = 20  # lighting pin
button_pin = 21  # button pin

# corrections due to different motor speeds
left_correction = 1
right_correction = 1

# update limit for sensor values
last_update_time = time.perf_counter()


def switch_lights(light_on):
    if light_on:
        light.off()
    else:
        light.on()


def servo_pos(pos):
    servo_states = ["lower arm", "raise arm left", "raise arm right", "open gate 1", "close gate 1", "open gate 2", "close gate 2"]
    print(f"Servo position: {servo_states[pos - 1]}")
    # lower arm
    if pos == 1:
        servo_1.off()
        servo_2.on()
        servo_3.off()
    # raise arm left
    elif pos == 2:
        servo_1.on()
        servo_2.off()
        servo_3.off()
    # raise arm right
    elif pos == 3:
        servo_1.on()
        servo_2.on()
        servo_3.off()
    # open gate 1
    elif pos == 4:
        servo_1.on()
        servo_2.on()
        servo_3.on()
    # close gate 1
    elif pos == 5:
        servo_1.off()
        servo_2.on()
        servo_3.on()
    # open gate 2
    elif pos == 6:
        servo_1.off()
        servo_2.off()
        servo_3.on()
    # close gate 2
    elif pos == 7:
        servo_1.on()
        servo_2.off()
        servo_3.on()

    servo_control.off()
    time.sleep(0.4)
    servo_control.on()


def steer(angle=190., speed=0.8):
    speed_left.value = 0
    speed_right.value = 0

    # stop
    if angle == 190:
        forward_right.off()
        backward_right.off()
        forward_left.off()
        backward_left.off()
        speed_left.value = 0
        speed_right.value = 0

    # backward
    elif angle == 200:
        forward_right.on()
        backward_right.off()
        forward_left.on()
        backward_left.off()
        speed_left.value = max(speed * left_correction, 0)
        speed_right.value = max(speed * right_correction, 0)

    # forward
    elif angle in range(-180, 181):
        forward_right.off()
        backward_right.on()
        forward_left.off()
        backward_left.on()

        # right
        if angle >= 0:
            if angle > max_turn_angle:
                forward_right.on()
                backward_right.off()
                forward_left.off()
                backward_left.on()
                speed_left.value = min(speed * left_correction * 1.2, 1)
                speed_right.value = min(speed * right_correction * 1.2, 1)
            else:
                speed_left.value = min(speed * left_correction, 1)
                speed_right.value = min(speed * right_correction * ((max_turn_angle - angle) / (max_turn_angle - 1)), 1)

        # left
        else:
            if angle < -max_turn_angle:
                forward_right.off()
                backward_right.on()
                forward_left.on()
                backward_left.off()
                speed_left.value = min(speed * left_correction * 1.2, 1)
                speed_right.value = min(speed * right_correction * 1.2, 1)
            else:
                speed_left.value = min(speed * left_correction * ((max_turn_angle + angle) / (max_turn_angle - 1)), 1)
                speed_right.value = min(speed * right_correction, 1)


def program_continue():
    switch.value = True if button.value == 1 else False
    return switch.value and not terminate.value


def update_sensor_average():
    global time_sensor_one, time_sensor_two, time_sensor_three, time_sensor_four, time_sensor_five, time_sensor_six, time_sensor_seven, time_last_gyro_y, time_last_gyro_x, time_last_gyro_z, time_silver_detected, time_silver_angle, time_victim_type, time_line_similarity, time_zone_similarity, last_update_time, time_exit_angle

    if time.perf_counter() - last_update_time > 1 / 90:
        if sensor_one.value > 25 or objective.value == "zone":
            time_sensor_one = add_time_value(time_sensor_one, sensor_one.value)
        if sensor_two.value > 25 or objective.value == "zone":
            time_sensor_two = add_time_value(time_sensor_two, sensor_two.value)
        time_sensor_three = add_time_value(time_sensor_three, sensor_three.value)
        time_sensor_four = add_time_value(time_sensor_four, sensor_four.value)
        if sensor_five.value > 25 or objective.value == "zone":
            time_sensor_five = add_time_value(time_sensor_five, sensor_five.value)
        time_sensor_six = add_time_value(time_sensor_six, sensor_six.value)
        time_sensor_seven = add_time_value(time_sensor_seven, sensor_seven.value)

        time_last_gyro_y = add_time_value(time_last_gyro_y, sensor_y.value)
        time_last_gyro_x = add_time_value(time_last_gyro_x, sensor_x.value)
        time_last_gyro_z = add_time_value(time_last_gyro_z, sensor_z.value)

        time_silver_detected = add_time_value(time_silver_detected, silver_value.value)

        time_silver_angle = add_time_value(time_silver_angle, silver_angle.value)
        time_exit_angle = add_time_value(time_exit_angle, exit_angle.value)

        if ball_type.value == 'silver ball':
            time_victim_type = add_time_value(time_victim_type, 1)
        elif ball_type.value == 'black ball':
            time_victim_type = add_time_value(time_victim_type, 0)

        time_line_similarity = add_time_value(time_line_similarity, line_similarity.value)
        time_zone_similarity = add_time_value(time_zone_similarity, zone_similarity.value)
        zone_similarity_average.value = round(get_time_average(time_zone_similarity, 15), 2)

        last_update_time = time.perf_counter()


def round_angle(angle, direction=0, rounding_value=90, final_addition=0, round_45_only=False):
    angle = (angle + direction) % 360
    if round_45_only:
        possible_angles = [45, 135, 225, 315]
        angle = min(possible_angles, key=lambda x: abs(x - angle))
    else:
        angle = round(angle / rounding_value) * rounding_value % 360
    return (angle + final_addition) % 360


def get_rotation():
    if rotation_y.value == "ramp_up":
        if get_time_average(time_last_gyro_y, .7) > 10:
            timer.set_timer("was_ramp_up", .7)
            return "ramp_up"
        elif get_time_average(time_last_gyro_y, .5) < -5.5:
            return "ramp_down"
        else:
            return "none"
    else:
        if get_time_average(time_last_gyro_y, .5) > 15:
            timer.set_timer("was_ramp_up", .7)
            return "ramp_up"
        elif get_time_average(time_last_gyro_y, .5) < -11:
            return "ramp_down"
        else:
            return "none"


def get_speed(angle):
    if rotation_y.value == "ramp_up":
        if abs(angle) > max_turn_angle:
            if not timer.get_timer("stuck_detected"):
                return .75
            else:
                return .6
        elif abs(angle) > max_turn_angle / 2:
            if not timer.get_timer("stuck_detected"):
                return .9
            else:
                return .75
        else:
            if not timer.get_timer("stuck_detected"):
                return .9
            else:
                return .65

    elif rotation_y.value == "ramp_down":
        if abs(angle) > max_turn_angle:
            return .65 if timer.get_timer("stuck_detected") else .85
        elif abs(angle) > max_turn_angle / 2:
            return .28 if timer.get_timer("stuck_detected") else .65
        else:
            return .15 if timer.get_timer("stuck_detected") else .3

    elif ramp_ahead.value or not timer.get_timer("ramp_ahead"):
        if ramp_ahead.value:
            timer.set_timer("ramp_ahead", 2)

        if abs(angle) > max_turn_angle:
            return .65
        elif abs(angle) > max_turn_angle / 2:
            return .4
        else:
            return .3

    return 1


def add_angle(angle, addition):
    return (angle + addition) % 360


def sub_angle(angle, subtraction):
    return (angle - subtraction) % 360


def turn_to_angle(angle, tolerance=1.5, stop_on_black=False, stop_on_victim=False, direction="n", speed=0, correct_overturn=True, stop_on_corner=False):
    global time_last_gyro_x

    start_angle = sensor_x.value
    last_angle = 400
    timer.set_timer("detect_stuck", 1.5)
    while abs((angle - sensor_x.value + 540) % 360 - 180) > tolerance:
        update_sensor_average()

        if direction == "n":
            angle_to_turn = (angle - sensor_x.value + 540) % 360 - 180
        elif direction == "r":
            angle_to_turn = (angle - sensor_x.value) % 360
            if last_angle < (angle_to_turn - 10):
                direction = "n"
        elif direction == "l":
            angle_to_turn = (angle - sensor_x.value) % -360
            if -last_angle > (angle_to_turn + 10):
                direction = "n"

        turn_direction = 180 if angle_to_turn > 0 else -180

        if angle_to_turn <= 0 and turn_direction == 180:
            time.sleep(.2)
            turn_direction = -180
        elif angle_to_turn > 0 and turn_direction == -180:
            time.sleep(.2)
            turn_direction = 180

        if speed == 0:
            steer(turn_direction, max(1 - pow(abs(abs(angle_to_turn) / 360 - 1), 7), 0.4))
        else:
            steer(turn_direction, speed)

        last_angle = abs(angle_to_turn)

        # if stuck
        if isclose(get_time_average(time_last_gyro_x, .5), sensor_x.value, abs_tol=.5) and not get_time_average(time_last_gyro_x, 1) == -1 and abs((angle - sensor_x.value + 540) % 360 - 180) > 20 and timer.get_timer("detect_stuck"):
            steer(-turn_direction, .9)
            time.sleep(.5)
            steer(turn_direction, .9)
            time.sleep(.8)
            steer()

            timer.set_timer("detect_stuck", 2)

        if stop_on_black and line_detected.value:
            steer()
            return "black"

        if stop_on_victim and ball_type.value != "none":
            steer()
            return "victim"

        if stop_on_corner and corner_distance.value != -181:
            steer()
            return "corner"

        if not correct_overturn and abs((angle - sensor_x.value + 540) % 360 - 180) < (2 * tolerance):
            steer()
            return "none"

        if not program_continue():
            return

    steer()
    return "none"


def turn_360(speed=0.6, stop_when_victim=False, stop_when_corner=False):
    timer.set_timer("turn_360_stuck", 15)
    for _ in range(2):
        current_angle = (sensor_x.value - 3) % 360

        while program_continue():
            update_sensor_average()

            if ((current_angle + 180) % 360 - sensor_x.value + 540) % 360 - 180 < 0:
                break

            if stop_when_victim and ball_type.value != "none" or stop_when_corner and corner_distance.value != -181:
                steer()
                return True

            if zone_stuck_detected() or timer.get_timer("turn_360_stuck"):
                avoid_stuck_zone()
                return False

            steer(180, speed)

    steer()
    if stop_when_victim or stop_when_corner:
        return False


def drive_until_wall(time_to_drive, speed=0.65, stop_when_wall=True, stop_when_near_wall=False, stop_when_near_corner=False, stop_when_corner=False, stop_when_black=False, stop_when_silver=False, stop_when_victim=False, stop_when_exit=False, exit_cooldown_time=0, return_driven_time=False, drift=0):
    global time_sensor_four

    corner_distance.value = -181
    timer.set_timer("drive_until_wall", time_to_drive)
    timer.set_timer("exit_cooldown", exit_cooldown_time)

    start_time = time.perf_counter()

    reason = "none"
    while not timer.get_timer("drive_until_wall"):
        update_sensor_average()
        steer(drift, speed)

        if stop_when_wall and wall_detected():
            reason = "wall"

        if stop_when_near_wall and near_wall_detected():
            reason = "near_wall"

        if stop_when_near_corner and get_time_average(time_sensor_five, 0.25) < 350:
            reason = "near_corner"

        if stop_when_corner and (zone_found_green.value or zone_found_red.value):
            reason = "corner"

        if stop_when_black and zone_found_black.value:
            reason = "black"

        if stop_when_silver and silver_detected() and False:
            reason = "silver"

        if stop_when_victim and ball_type.value != "none":
            reason = "ball"

        if timer.get_timer("exit_cooldown"):
            if stop_when_exit and get_time_average(time_sensor_four, 0.25) > 180:
                reason = "exit"
        else:
            time_sensor_four = empty_time_arr()

        if not program_continue() or not reason == "none":
            break

    steer()

    return reason if not return_driven_time else (reason, time.perf_counter() - start_time)


def drive_back_until_line(max_time, speed=.7):

    timer.set_timer("find_line_again", max_time)
    while not line_detected.value and not timer.get_timer("find_line_again"):
        steer(200, speed)
        time.sleep(.001)
    min_line_size.value = 3000

    steer(0, .7)
    time.sleep(.2)
    steer()

    return line_detected.value


def ensure_line_detected():
    time.sleep(.25)
    if not line_detected.value:
        steer(200, .7)
        time.sleep(.15)
        steer()
        time.sleep(.1)

        if not line_detected.value:
            return False

    return True


def orientate_gap():
    update_sensor_average()
    if (not line_detected.value or line_detected.value and line_size.value < 17000) and not silver_detected():
        status.value = f'Validating gap'

        steer(200, .7)
        time.sleep(.15)
        steer()
        time.sleep(.2)

        update_sensor_average()
        if silver_detected():
            steer(0, .7)
            time.sleep(.15)
            steer()
            time.sleep(.2)
            return False

        if obstacle_detected():
            return False

        steer(200, .7)
        time.sleep(.3)
        if not line_detected.value:
            time.sleep(.2)

        steer(0, .7)
        time.sleep(.25)
        steer()

    update_sensor_average()
    if line_detected.value and black_average.value < 40 and not silver_detected():
        status.value = f'Orientating at gap'

        angle = gap_angle.value
        x_gap = gap_center_x.value
        y_gap = gap_center_y.value

        correction_counter = 0
        while correction_counter < 7:

            if y_gap < 10:
                return False

            time_foreward = .25

            if (0 < angle < 173 and x_gap < 0) or (angle < -7 and x_gap > 0) or (0 < angle < 155) or (angle < -25):
                min_time = .35

                if (0 < angle < 173 and x_gap < 0) or (angle < -7 and x_gap > 0):
                    x_gap_perc = pow(abs(x_gap) / (180 + 40), .7)
                else:
                    x_gap_perc = 0

                y_gap_perc = y_gap / camera_y

                if angle > 0:
                    angle_perc = (angle - 90) / 90
                else:
                    angle_perc = abs(-angle / 90)

                time_foreward = min_time + .3 * x_gap_perc + .1 * y_gap_perc + .3 * angle_perc

            if not (0 >= angle > -1 or angle > 179):
                steer(0, .7)
                time.sleep(time_foreward)

                if not program_continue():
                    return False

                if angle > 0:
                    steer(180, .65)
                    time.sleep(abs(.9 - .85 * ((angle - 90) / 90)))
                else:
                    steer(-180, .65)
                    time.sleep(abs(.05 + .85 * abs(-angle / 90)))

                steer()

                if not program_continue():
                    return False

                min_line_size.value = 9000
                steer(200, .7)
                time.sleep(time_foreward + np.clip(((time_foreward - .25) / .4) * .15, 0, .15))

                if not drive_back_until_line(.6, .7):
                    return False

                if line_size.value > 17000:
                    steer(200, .7)
                    time.sleep(.2)
                    steer()
                    return False

            if not ensure_line_detected() or not program_continue():
                return False

            angle = gap_angle.value
            x_gap = gap_center_x.value

            if y_gap < 10:
                return False

            if abs(x_gap) > 55:
                steer(180 if x_gap > 0 else -180, .6)
                time.sleep(.4)
                steer()
                time.sleep(.2)

                time_foreward = .35 + .35 * ((abs(x_gap) - 55) / 100)

                steer(0, .7)
                time.sleep(time_foreward)
                steer()

                if not program_continue():
                    return False

                steer(-180 if x_gap > 0 else 180, .6)
                time.sleep(.3)
                steer()
                time.sleep(.2)

                if not program_continue():
                    return False

                min_line_size.value = 9000
                steer(200, .7)
                time.sleep(time_foreward + np.clip(((time_foreward - .35) / .35) * .2, 0, .2))

                if not drive_back_until_line(.5, .7):
                    return False

                if line_size.value > 17000:
                    steer(200, .7)
                    time.sleep(.2)
                    steer()
                    return False

                if not ensure_line_detected() or not program_continue():
                    return False

                angle = gap_angle.value
                x_gap = gap_center_x.value

                if y_gap < 10:
                    return False

            if (0 >= angle > -1 or angle > 179) and abs(x_gap) < 140:
                break

            if not program_continue():
                return False

            correction_counter += 1

        status.value = f'Gap orientated'
        line_status.value = "gap_avoid"
        min_line_size.value = 4000
        steer(0, .7)
        time.sleep(.8)
        return True

    elif (line_detected.value and black_average.value > 40) or silver_detected():
        status.value = f'Validation failed'
        if line_detected.value and black_average.value > 40:
            steer(200, .7)
            time.sleep(.2)
            steer()
        return False

    else:
        status.value = f'Searching for the line'

        start_angle = sensor_x.value

        reason = turn_to_angle(add_angle(sensor_x.value, 45), 1.5, True, False, "r", 0.6, False)

        if reason == "black" or not program_continue():
            return False

        reason = turn_to_angle(sub_angle(sensor_x.value, 90), 1.5, True, False, "l", 0.6, False)

        if reason == "black" or not program_continue():
            return False

        turn_to_angle(start_angle, 1.5)

        timer.set_timer("line_search", 1.2)
        while not line_detected.value and not timer.get_timer("line_search") and program_continue():
            steer(0, .7)
            time.sleep(.001)

        steer()
        return False


def turn_around():
    average_sensor_z = get_time_average(time_last_gyro_z, 1)
    if (-135 > average_sensor_z > -165 or 130 < average_sensor_z < 160) and turn_around_ramp_side and rotation_y.value == "none":
        steer(0, .7)
        time.sleep(.15)
        steer(-180, .6)
        time.sleep(.15)
        steer(0, .8)
        time.sleep(.15)
        steer(-180, .6)
        time.sleep(.2)
        steer(0, .8)
        time.sleep(.2)
        steer(-180, .6)
        time.sleep(.4)
        steer(0, .8)
        time.sleep(.3)
        steer(-180, .6)
        time.sleep(.4)
        steer(0, .8)
        time.sleep(.6)
        steer(-180, .6)
        time.sleep(.4)
        steer(0, .8)
        time.sleep(.4)
        steer(-180, .6)
        time.sleep(.4)
        steer(0, .8)
        time.sleep(.2)
        steer(-180, .6)
        time.sleep(.4)

    else:
        was_ramp_up = rotation_y.value == "ramp_up" or not timer.get_timer("was_ramp_up")
        steer(0, .7)
        time.sleep(.85 if was_ramp_up else .55)

        turn_to_angle(round_angle(sensor_x.value, 180, 90 if not turn_around_45 else 45), direction=last_turn_dir)

        steer(200, .7)
        time.sleep(.2 if was_ramp_up else .3)
        steer()

        if line_size.value < 5500:
            steer(200, .7)
            time.sleep(.4)
            steer()

    timer.set_timer("stuck_cooldown", 5)

    return "r" if last_turn_dir == "l" else "l"


def obstacle_detected():
    if ((20 < get_time_average(time_sensor_one, 0.25) < 75 or 20 < get_time_average(time_sensor_two, 0.25) < 55 or 20 < get_time_average(time_sensor_five, 0.25) < 55) and (rotation_y.value == "none" or obstacle_on_ramp)) and timer.get_timer("obstacle_detect_cooldown") and print_obstacle:
        print("Obstacle: ", get_time_average(time_sensor_one, 0.25), get_time_average(time_sensor_two, 0.25), get_time_average(time_sensor_five, 0.15))
    return ((20 < get_time_average(time_sensor_one, 0.25) < 75 or 20 < get_time_average(time_sensor_two, 0.25) < 55 or 20 < get_time_average(time_sensor_five, 0.25) < 55) and (rotation_y.value == "none" or obstacle_on_ramp)) and timer.get_timer("obstacle_detect_cooldown")


def obstacle_detected_again():
    return ((20 < get_time_average(time_sensor_one, 0.25) < 75 or 20 < get_time_average(time_sensor_two, 0.25) < 55 or 20 < get_time_average(time_sensor_five, 0.25) < 95) and (rotation_y.value == "none" or obstacle_on_ramp)) and timer.get_timer("obstacle_detect_cooldown")


def wall_detected():
    if ((0 < get_time_average(time_sensor_one, 0.25) < 75 or 0 < get_time_average(time_sensor_two, 0.25) < 55 or 0 < get_time_average(time_sensor_five, 0.25) < 95)) and print_obstacle:
        print("Wall: ", get_time_average(time_sensor_one, 0.25), get_time_average(time_sensor_two, 0.25), get_time_average(time_sensor_five, 0.15))
    return ((0 < get_time_average(time_sensor_one, 0.25) < 75 or 0 < get_time_average(time_sensor_two, 0.25) < 55 or 0 < get_time_average(time_sensor_five, 0.25) < 95))


def near_wall_detected():
    return ((0 < get_time_average(time_sensor_one, 0.25) < 135 or 0 < get_time_average(time_sensor_two, 0.25) < 135 or 0 < get_time_average(time_sensor_five, 0.25) < 150))


def distance_left():
    return (get_time_average(time_sensor_three, 0.25))


def distance_right():
    return (get_time_average(time_sensor_four, 0.25))


def turn_for_obstacle():
    global time_sensor_one, time_sensor_two, time_sensor_five

    if rotation_y.value == "none":
        sensor_one_avg = get_time_average(time_sensor_one, 0.15)
        sensor_two_avg = get_time_average(time_sensor_two, 0.15)

        steer(200, .7)
        time.sleep(.15)
        steer()

        # centering in front of obstacle
        update_sensor_average()
        if get_time_average(time_sensor_five, 0.15) > 130:
            status.value = f'Centering in front of obstacle'

            turn_direction = 180 if sensor_one_avg < sensor_two_avg else -180

            timer.set_timer("obstacle", 5)
            while get_time_average(time_sensor_five, 0.15) > 130:
                update_sensor_average()

                steer(turn_direction, .55)

                if timer.get_timer("obstacle"):
                    return False

                if not program_continue():
                    return False

            steer(-turn_direction, .55)
            time.sleep(.15)

        steer()
        time.sleep(.5)

        # correcting distance to obstacle
        update_sensor_average()
        if 0 < get_time_average(time_sensor_five, 0.15) < 180:
            status.value = f'Correcting distance to obstacle'

            timer.set_timer("obstacle", 3)
            while not 75 < get_time_average(time_sensor_five, 0.15) < 90:
                update_sensor_average()

                if get_time_average(time_sensor_five, 0.15) > 90:
                    steer(0, .55)
                elif get_time_average(time_sensor_five, 0.15) < 75:
                    steer(200, .55)

                if timer.get_timer("obstacle"):
                    return False

                if not program_continue():
                    return False

            steer()

        turn_direction = -180 if obstacle_dir[obstacle_count % len(obstacle_dir)] == "l" else 180

        # turning to avoid obstacle
        timer.set_timer("obstacle", 5)
        if 70 < get_time_average(time_sensor_five, 0.15) < 95:
            while 0 < get_time_average(time_sensor_five, 0.15) < 280:
                status.value = f'Turning to avoid obstacle'

                update_sensor_average()

                steer(turn_direction, .65)

                if timer.get_timer("obstacle"):
                    return False

                if not program_continue():
                    return False

            steer(turn_direction, .65)
            time.sleep(.3)

            steer(0, .55)
            time.sleep(.45)

            steer()
            return True

        else:
            return False

    else:

        if rotation_y.value == "ramp_down":
            steer(200, .5)
            time.sleep(.3)
            steer(200, .2)
        elif rotation_y.value == "ramp_up":
            steer()
            time.sleep(.5)
            steer(200, .25)
            time.sleep(.3)
            steer(0, .15)

        time.sleep(.5)

        update_sensor_average()
        if obstacle_detected_again():
            turn_direction = -180 if obstacle_dir[obstacle_count % len(obstacle_dir)] == "l" else 180

            if rotation_y.value == "ramp_down":
                steer(200, .7)
                time.sleep(.7)

            steer(turn_direction, .75)

            if rotation_y.value == "ramp_up":
                time.sleep(.5)
            else:
                time.sleep(.65)

            if rotation_y.value == "ramp_up":
                steer(0, .8)
                time.sleep(.3)

            steer()
            return True

        else:
            return False


def return_after_failed_obstacle(start_angle):
    turn_to_angle(start_angle, 1.5)
    steer(200, .7)
    time.sleep(.25)
    steer()


def orientate_after_obstacle(direction):
    steer(0, .7)
    time.sleep(.1)
    steer()

    start_angle = sensor_x.value

    steer(180 if direction == "l" else -180, .7)
    time.sleep(.4)
    steer()
    time.sleep(.2)

    steer(0, .7)
    time.sleep(.75)
    steer()
    time.sleep(.2)

    steer(-180 if direction == "l" else 180, .7)
    time.sleep(.4)
    timer.set_timer("obstacle_turn", 3)
    while not line_detected.value and not timer.get_timer("obstacle_turn"):
        time.sleep(.01)

        if not program_continue():
            return

    if not timer.get_timer("obstacle_turn"):
        time.sleep(.35)
        steer()
        time.sleep(.2)

        if line_detected.value:
            return

        steer(180 if direction == "l" else -180, .7)
        time.sleep(.2)
        steer()
        time.sleep(.2)

        if line_detected.value:
            return

    turn_to_angle(start_angle, 1.5)

    if line_detected.value:
        return

    steer(200, .7)
    time.sleep(.85)
    steer()
    time.sleep(.2)
    return


def seesaw_detected():
    return get_time_average(time_last_gyro_y, .6) > 6.5 and sensor_y.value < -10


def avoid_seesaw():
    steer(200, .7)
    time.sleep(.15)
    steer(200, .1)
    time.sleep(2)

    steer(200, .7)
    time.sleep(.2)
    if not line_detected.value:
        time.sleep(.3)


last_rotation = "none"


def ramp_down_detected():
    global last_rotation
    is_ramp_down = last_rotation == "none" and rotation_y.value == "ramp_down"
    last_rotation = rotation_y.value
    return is_ramp_down


def zone_stuck_detected():
    return get_time_average(time_zone_similarity, 15) >= .95 and timer.get_timer("zone_stuck_cooldown")


def avoid_stuck():
    status.value = f'Line similarity too high, stuck detected'

    angle = line_angle.value

    if rotation_y.value == "none" and line_status.value == "line_detected" and abs(angle) > 120:
        steer()
        time.sleep(1)
        steer(180 if angle < 0 else -180, .7)
        time.sleep(.35)
        steer(0, .7)
        time.sleep(.45)
        steer(-180 if angle < 0 else 180, .7)
        time.sleep(.45)
        steer(200, .7)
        time.sleep(.5)

    elif rotation_y.value == "ramp_down":
        steer()
        time.sleep(1)
        steer(200, .7)
        time.sleep(.5)
        steer()

    else:
        steer()
        time.sleep(.5)

    timer.set_timer("stuck_detected", 1.2 if rotation_y.value == "ramp_up" else .85)


def avoid_stuck_zone():
    status.value = f'Image similarity too high, stuck detected'
    steer()
    time.sleep(1)
    steer(200, .7)
    time.sleep(.5)
    steer()
    steer(random.choice([-180, 180]), .6)
    time.sleep(1)
    drive_until_wall(1.5, .7, stop_when_black=True, stop_when_silver=True)
    timer.set_timer("zone_stuck_cooldown", 4)


def stop_for_red():
    steer()
    for i in range(wait_time_red):
        if not program_continue():
            break

        if i == 5:
            run_start_time.value = -1

        status.value = f'Waiting for red: {wait_time_red - i} seconds left'
        time.sleep(1)

        if i == wait_time_red - 1:
            steer(0, 55)
            time.sleep(.5)
            steer()


def wait_time(time_to_wait, message, rotation="n"):
    if rotation == "u":
        steer(0, .2)
    elif rotation == "d":
        steer(200, .2)
    else:
        steer()

    for i in range(time_to_wait):
        if not program_continue():
            return False

        status.value = f'Waiting for {message}: {time_to_wait - i} seconds left'
        time.sleep(1)

    return program_continue()


def silver_detected():
    return get_time_average(time_silver_detected, .15 if rotation_y.value == "ramp_down" else .25) > .7 and not zone_done and timer.get_timer("silver_cooldown")


def validate_silver():
    status.value = f'Validating silver line'

    if rotation_y.value == "ramp_down":
        steer(200, .5)
        time.sleep(.3)
        steer(200, .2)
        time.sleep(.7)
        steer(200, .6)
        time.sleep(.45)
        steer()
    elif rotation_y.value == "ramp_up":
        pass
    else:
        steer(200, .7)
        time.sleep(.15)
        steer()

    if rotation_y.value == "ramp_down":
        steer(200, .2)
    elif rotation_y.value == "ramp_up":
        steer(0, .2)
    else:
        steer()

    time.sleep(.25 if speed_zone else .5)

    prev_line_size = black_average.value

    line_status.value = "check_silver"

    switch_lights(False)

    time.sleep(1.5 if speed_zone else 1.7)

    # print(f"Prev: {prev_line_size}, Current: {black_average.value}")
    if black_average.value > max(prev_line_size - 23, 0):
        status.value = f'Validating silver line failed'
        line_status.value = "line_detected"
        switch_lights(True)

        time.sleep(1)

        return False
    else:
        status.value = f'Validating silver line successful'
        if not speed_zone:
            time.sleep(.4)
        return True


def calculate_distance_nearest_90(current_angle):
    nearest_90 = round(current_angle / 90) * 90
    return nearest_90 - current_angle


def position_for_entry():
    tolerance = 10
    status.value = f'Centering silver line'

    if not line_detected.value or line_angle_y.value < camera_y * .1:
        timer.set_timer("entry", .75)
        while not line_detected.value and line_angle_y.value < camera_y * .1 and not timer.get_timer("entry") and program_continue():
            steer_direction = 200 if not line_detected.value else 0
            steer(steer_direction, .4)

        steer(0, .1)
        time.sleep(.3)
        steer()

    direction = 0
    if abs(calculate_distance_nearest_90(sensor_x.value)) > 15:
        status.value = f'Rotation not straight, determining silver angle'

        line_status.value = "position_entry_1"
        time.sleep(1.5)
        line_status.value = "position_entry"
        switch_lights(True)
        time.sleep(1)
        line_status.value = "position_entry_2"
        time.sleep(1.3)

        start_time = time.perf_counter()
        while not time.perf_counter() - start_time > .7:
            update_sensor_average()

        angle_silver = get_time_average(time_silver_angle, .25)
        line_status.value = "position_entry"

        if angle_silver > 20:
            direction = -35
        elif 0 > angle_silver > -160:
            direction = 35

        status.value = f'Got silver angle: {round(angle_silver, 2)}°'
        switch_lights(False)
        time.sleep(1)

    status.value = f'Centering black line'

    last_line_angle_y = line_angle_y.value
    timer.set_timer("center_black", 2)
    while not -tolerance < line_angle.value < tolerance and not timer.get_timer("center_black"):
        if line_detected.value:
            last_line_angle_y = line_angle_y.value

        if line_angle_y.value < camera_y * .1 or (not line_detected.value and last_line_angle_y < camera_y / 2):
            steer(0, .30)
        elif line_angle_y.value > camera_y * .9 or (not line_detected.value and last_line_angle_y > camera_y / 2):
            steer(200, .30)
        else:
            turn_direction = 180 if line_angle.value > 0 else -180

            steer(turn_direction, max(1 - pow(abs(abs(abs(line_angle.value)) / 180 - 1), 1.7), 0.4))

        if not program_continue():
            return False

    steer(0, .65)
    time.sleep(.35)

    status.value = f'Turning into entry'
    turn_to_angle(round_angle(sensor_x.value, direction=direction))

    return True


turn_360_counter = 0


def search_for_victims():
    global turn_360_counter

    while program_continue():
        if turn_360(speed=.7 if speed_zone else .6, stop_when_victim=True) and turn_360_counter < 4:
            turn_360_counter += 1
            break
        elif timer.get_timer("max_search_time"):
            break
        else:
            turn_360_counter = 0
            steer(random.choice([-180, 180]), .6)

            start_time = time.perf_counter()
            while time.perf_counter() - start_time < random.uniform(1.5, 2.5) and program_continue():
                if ball_type.value != "none":
                    steer()
                    break

            stop_reason = drive_until_wall(random.uniform(1, 2), stop_when_black=True, stop_when_silver=True, stop_when_victim=True)

            if stop_reason in ["silver", "black", "wall"] and program_continue():
                steer(200, .6)
                time.sleep(1)
                turn_to_angle(angle=add_angle(sensor_x.value, 120), tolerance=7, stop_on_victim=True)
                drive_until_wall(1, stop_when_black=True, stop_when_silver=True, stop_when_victim=True)

    steer()


def search_for_corner():
    while program_continue():
        global turn_360_counter

        if turn_360(speed=.85 if speed_zone else .65, stop_when_corner=True) and turn_360_counter < 4:
            turn_360_counter += 1
            break
        else:
            turn_360_counter = 0
            steer(random.choice([-180, 180]), .6)

            start_time = time.perf_counter()
            while time.perf_counter() - start_time < random.uniform(1, 2) and program_continue():
                if corner_distance.value != -181:
                    steer()
                    break

            stop_reason = drive_until_wall(random.uniform(1.5, 2.5), stop_when_black=True, stop_when_silver=True)

            if stop_reason in ["silver", "black", "wall"] and program_continue():
                steer(200, .6)
                time.sleep(.4)
                turn_to_angle(angle=add_angle(sensor_x.value, 120), tolerance=7, stop_on_corner=True)
                drive_until_wall(1, stop_when_black=True, stop_when_silver=True)

    steer()


def turn_to_victim(tolerance=10):
    timer.set_timer("turn_to_victim_stuck", 15)
    timer.set_timer("turn_to_victim", .6)
    while program_continue() and not -tolerance <= ball_distance.value <= tolerance and (ball_type.value != "none" or not timer.get_timer("turn_to_victim")):
        status.value = f"Turning to {'alive' if ball_type.value == 'silver ball' else 'dead'} victim"

        update_sensor_average()

        direction = 180 if ball_distance.value > 0 else -180

        steer(direction, max(1 - pow(abs(abs(ball_distance.value / 2) / (camera_x / 2) - 1), 3), 0.4))

        if zone_stuck_detected() or timer.get_timer("turn_to_victim_stuck"):
            avoid_stuck_zone()
            return False

        if ball_type.value != "none":
            timer.set_timer("turn_to_victim", .6)

    steer()

    if not program_continue() or ball_type.value == "none":
        if program_continue():
            steer(0)
            time.sleep(.3)
            steer()
        return False
    else:
        return True


def turn_to_corner(color, tolerance=10):
    timer.set_timer("turn_to_corner_stuck", 15)
    timer.set_timer("turn_to_corner", .6)
    while program_continue() and not -tolerance <= corner_distance.value <= tolerance and (corner_distance.value != -181 or not timer.get_timer("turn_to_corner")):
        status.value = f"Turning to {color} evacuation point"

        update_sensor_average()

        direction = 180 if corner_distance.value > 0 else -180

        steer(direction, max(1 - pow(abs(abs(corner_distance.value) / (camera_x / 2) - 1), 5), 0.4))

        if zone_stuck_detected() or timer.get_timer("turn_to_corner_stuck"):
            avoid_stuck_zone()
            return False

        if corner_distance.value != -181:
            timer.set_timer("turn_to_corner", .6)

    steer()

    if not program_continue() or corner_distance.value == -181:
        steer(0)
        time.sleep(.3)
        steer()
        return False
    else:
        return True


def drive_to_victim(speed=0.6):
    timer.set_timer("drive_to_victim_stuck", 15)
    timer.set_timer("drive_to_victim", .6)
    while ball_width.value < 140 if speed_zone else 200:
        status.value = f"Driving to {'alive' if ball_type.value == 'silver ball' else 'dead'} victim"

        update_sensor_average()

        steer_angle = int(max(min(ball_distance.value, max_turn_angle), -max_turn_angle))
        steer(steer_angle, speed)

        if (ball_type.value == "none" and timer.get_timer("drive_to_victim")) or not program_continue():
            steer()
            return False

        if zone_stuck_detected() or timer.get_timer("drive_to_victim_stuck"):
            avoid_stuck_zone()
            return False

        if ball_type.value != "none":
            timer.set_timer("drive_to_victim", .6)

    steer()
    return True


def drive_to_corner(color, speed=0.6):
    status.value = f'Driving to {color} evacuation point'

    timer.set_timer("drive_to_corner_stuck", 15)
    timer.set_timer("drive_to_corner", .6)
    while corner_size.value < 140:

        update_sensor_average()

        steer_angle = int(max(min(2 * corner_distance.value, max_turn_angle), -max_turn_angle))
        steer(steer_angle, speed)

        if (corner_distance.value == -181 and timer.get_timer("drive_to_corner")) or abs(corner_distance.value) > 60 or not program_continue():
            steer()
            return False

        if zone_stuck_detected() or timer.get_timer("drive_to_corner_stuck"):
            avoid_stuck_zone()
            return False

        if corner_distance.value != -181:
            timer.set_timer("drive_to_corner", .6)

    steer(200, .7)
    time.sleep(.15)
    steer()

    return True


def pick_up_victim(alive):

    servo_pos(1)

    steer(200, .7)
    time.sleep(.45)
    steer()

    time.sleep(.6 if speed_zone else 1.5)

    timer.set_timer("pickup", .5 if speed_zone else 1.15)
    while (get_time_average(time_sensor_seven, .2) > 75 or get_time_average(time_sensor_seven, .2) == -1) and not timer.get_timer("pickup"):
        update_sensor_average()

        steer(0, .65 if speed_zone else .5)

        if not program_continue():
            return False

    servo_pos(3 if alive and picked_up_alive_count.value < 2 else 2)
    time.sleep(.05)

    steer(200, 1)
    time.sleep(.25)
    steer()

    timer.set_timer("pickup", 1 if not speed_zone else .6)
    while not timer.get_timer("pickup"):
        update_sensor_average()

        if not program_continue():
            return False

    return get_time_average(time_sensor_seven, .2) < 50


def dump_victims(alive, dumped_victims=False):
    status.value = f"Positioning in front of evacuation point"

    if speed_zone:
        reason = drive_until_wall(2, speed=.9, stop_when_near_wall=True)

    else:
        switch_lights(True)
        time.sleep(1.5)

        reason = drive_until_wall(2, stop_when_wall=False, stop_when_corner=True)
        switch_lights(False)

        if reason != "corner":
            return False

    turn_to_angle(angle=add_angle(sensor_x.value, 180), direction=random.choice(["r", "l"]), tolerance=7 if speed_zone else 1.5)

    if program_continue():
        status.value = f"Dumping {'alive' if alive else 'dead'} victims"
        steer(200, 1)
        time.sleep(.8 if speed_zone else 2.75)
        steer()

        if program_continue():
            if not dumped_victims:
                servo_pos(4)
                time.sleep(.6)

                if not speed_zone:
                    time.sleep(.9)

                    steer(0, .7)
                    time.sleep(.35)
                    steer(200, 1)
                    time.sleep(.3)
                    steer()

                    time.sleep(1)

                servo_pos(5)

                if alive:
                    drive_until_wall(.7)
                    servo_pos(6)

            drive_until_wall(.15 if speed_zone else .3, speed=.9 if speed_zone else .65)

            return True

    return False


def validate_exit():
    status.value = f'Validating black line'

    steer()
    time.sleep(.3 if speed_zone else 1)

    prev_line_size = black_average.value

    zone_status.value = "check_silver"

    switch_lights(False)

    time.sleep(1 if speed_zone else 1.5)

    if black_average.value > max(prev_line_size - 23, 0):
        status.value = f'Validating black line successful'
        if not speed_zone:
            time.sleep(.5)
        return True

    else:
        status.value = f'Validating black line failed'

        switch_lights(True)

        steer(200, .65)
        time.sleep(.15)
        steer()

        turn_to_angle(round_angle(sensor_x.value, direction=-90))
        zone_status.value = "exit"
        return False


def find_exit():
    status.value = f'Searching next wall'

    steer(200, .65)
    time.sleep(.5)
    turn_to_angle(round_angle(sensor_x.value, direction=90, rounding_value=90, round_45_only=True), tolerance=7 if speed_zone else 1.5)

    check_exit = False
    drift_amount = 75
    exit_cooldown_time = 0

    first_run = True

    while program_continue():
        return_reason = drive_until_wall(10, speed=1 if speed_zone else .9, stop_when_corner=True, stop_when_black=True, stop_when_silver=True, stop_when_exit=check_exit, exit_cooldown_time=exit_cooldown_time, drift=drift_amount)

        if return_reason in ["black", "silver"]:
            status.value = f'Detected {return_reason} line in front'

            steer(200, .65)
            time.sleep(.1)
            steer()
            time.sleep(.2)

            steer(0, .6)
            time.sleep(.15)
            steer()
            time.sleep(.3)

            if validate_exit():
                return True

            status.value = f'Silver line detected, continuing to search for exit'
            check_exit = True
            drift_amount = 35

            if first_run:
                exit_cooldown_time = 1.6
            else:
                exit_cooldown_time = 1.3 if not speed_zone else 1.1


        elif return_reason == "exit":
            status.value = f'Detected exit on the right side'

            turn_to_angle(round_angle(sensor_x.value, direction=90), tolerance=7 if speed_zone else 1.5)

            steer(200, .65)
            time.sleep(.6 if speed_zone else 1)

            reason = drive_until_wall(2.5, stop_when_wall=True, stop_when_black=True, stop_when_silver=True)

            if reason in ["silver", "black"]:
                status.value = f'Detected {return_reason} line in front'

                steer(200, .65)
                time.sleep(.1)
                steer()
                time.sleep(.2)

                steer(0, .6)
                time.sleep(.15)
                steer()
                time.sleep(.3)

                if validate_exit():
                    return True

                status.value = f'Silver line detected, continuing to search for exit'

                check_exit = True
                drift_amount = 35
                exit_cooldown_time = 1.3

            elif reason == "wall":
                status.value = f'Wall detected, turning 90°'

                turn_to_angle(round_angle(sensor_x.value, direction=-90, final_addition=10), tolerance=7 if speed_zone else 1.5)

                check_exit = True
                drift_amount = 35
                exit_cooldown_time = 0

            elif reason == "none":
                status.value = f'Maximum distance reached, obstacle detected'

                turn_to_angle(round_angle(sensor_x.value, direction=90, final_addition=-15), tolerance=7 if speed_zone else 1.5)

                check_exit = False
                drift_amount = 0
                exit_cooldown_time = 0

        elif return_reason == "wall":
            status.value = f'Wall detected, turning 90°'

            turn_to_angle(round_angle(sensor_x.value, direction=-90, final_addition=10), tolerance=7 if speed_zone else 1.5)

            check_exit = True
            drift_amount = 35
            exit_cooldown_time = 0

        elif return_reason == "corner":
            status.value = f'Evacuation point detected, turning 45°'

            turn_to_angle(round_angle(sensor_x.value, direction=-90, final_addition=30), tolerance=7 if speed_zone else 1.5)

            reason = drive_until_wall(5, speed=.9, stop_when_black=True, stop_when_silver=True, drift=75)

            if reason == "wall":
                status.value = f'Wall detected, turning 90°'

                turn_to_angle(round_angle(sensor_x.value, direction=-55, final_addition=10), tolerance=7 if speed_zone else 1.5)

                check_exit = True
                drift_amount = 35
                exit_cooldown_time = 0

            elif reason in ["black", "silver"]:
                status.value = f'Detected {reason} line in front'

                steer(0, .65)
                time.sleep(.25)
                turn_to_angle(round_angle(sensor_x.value, direction=30), tolerance=7 if speed_zone else 1.5)

                steer(200, .65)
                time.sleep(1.4)

                reason = drive_until_wall(2.8, stop_when_wall=True, stop_when_black=True, stop_when_silver=True)

                if reason in ["silver", "black"]:
                    status.value = f'Detected {return_reason} line in front'

                    steer(200, .65)
                    time.sleep(.1)
                    steer()
                    time.sleep(.2)

                    steer(0, .6)
                    time.sleep(.15)
                    steer()
                    time.sleep(.3)

                    if validate_exit():
                        return True

                    status.value = f'Silver line detected, continuing to search for exit'

                    check_exit = True
                    drift_amount = 35
                    exit_cooldown_time = 1.3

                elif reason == "wall":
                    status.value = f'Wall detected, turning 90°'

                    turn_to_angle(round_angle(sensor_x.value, direction=-90, final_addition=10), tolerance=7 if speed_zone else 1.5)

                    check_exit = True
                    drift_amount = 35
                    exit_cooldown_time = 0

                elif reason == "none":
                    status.value = f'Maximum distance reached, obstacle detected'

                    turn_to_angle(round_angle(sensor_x.value, direction=90, final_addition=10), tolerance=7 if speed_zone else 1.5)

                    check_exit = False
                    drift_amount = 0
                    exit_cooldown_time = 0

        elif return_reason == "none":
            status.value = f'Stuck detected'

            time.sleep(.5)
            steer(200, 1)
            time.sleep(.4)
            steer()
            time.sleep(.5)
            steer(0, 1)
            time.sleep(.7)
            steer()

        first_run = False

    return False


def position_exit():
    start_time = time.perf_counter()

    while not time.perf_counter() - start_time > .7:
        update_sensor_average()

    angle_exit = get_time_average(time_exit_angle, .25)

    if angle_exit > 15:
        direction = -35
    elif 0 > angle_exit > -165:
        direction = 35
    else:
        direction = 0

    status.value = f'Got exit angle: {round(angle_exit, 2)}°'

    switch_lights(True)

    if direction != 0:
        status.value = f'Angle too high, turning into exit'
        turn_to_angle(round_angle(sensor_x.value, direction=direction))

    steer(0, .65)
    time.sleep(.35)
    steer()


# debug methods
def calibrate_turn_time():
    gyro_x_offset(0)

    last_gyro = 0
    for i in range(1, 300, 1):
        direction = 180 if i % 2 == 0 else -180
        steer(direction, .8)
        time.sleep(i / 100)
        steer()
        time.sleep(.5)

        print(f"{i / 100}: {round(((sensor_x.value - last_gyro + 540) % 360 - 180), 2)}")

        if not program_continue():
            break

        last_gyro = sensor_x.value


########################################################################################################################
# Main Control Loop
########################################################################################################################


def control_loop():
    global forward_right, backward_right, forward_left, backward_left, speed_right, speed_left, light, servo_control, servo_1, servo_2, servo_3, button
    global run, zone_done, dumped_alive_victims, dumped_dead_victims, last_turn_dir, obstacle_count, time_last_gyro_y, time_last_gyro_x, time_last_gyro_z, time_last_angles, time_sensor_one, time_sensor_two, time_sensor_three, time_sensor_four, time_sensor_five, time_sensor_six, time_sensor_seven, time_silver_detected, time_line_similarity, time_zone_similarity, time_victim_type

    # gpio setup
    forward_right = LED(in_1)
    backward_right = LED(in_2)
    forward_left = LED(in_3)
    backward_left = LED(in_4)

    speed_right = PWMLED(en_a, frequency=1000)
    speed_left = PWMLED(en_b, frequency=1000)

    servo_control = LED(servo_control_pin)
    servo_control.on()

    servo_1 = LED(servo_pin_1)
    servo_2 = LED(servo_pin_2)
    servo_3 = LED(servo_pin_3)

    light = LED(led)
    button = Button(button_pin)

    time.sleep(.5)

    switch_lights(True)

    servo_pos(5)
    time.sleep(.25)
    servo_pos(7)
    time.sleep(.25)

    calibration_switched_light = False
    obstacle_is_ramp = "none"
    iteration_limit_time = time.perf_counter()
    max_iterations = 60
    iteration_time = time.perf_counter()
    counter = 0

    timer.set_timer("silver_cooldown", .01)
    timer.set_timer("ramp_ahead", .01)
    timer.set_timer("stuck_detected", .01)
    timer.set_timer("obstacle_detect_cooldown", .01)
    timer.set_timer("stuck_cooldown", 5)
    timer.set_timer("zone_stuck_cooldown", 5)
    timer.set_timer("was_ramp_up", .01)

    while not terminate.value:
        if calibrate_color_status.value == "none":
            if calibration_switched_light:
                switch_lights(True)
                calibration_switched_light = False

            # update average time values
            update_sensor_average()

            # update runtime variables
            switch.value = True if button.value == 1 else False
            rotation_y.value = get_rotation()

            if not switch.value and run and objective.value == "debug":
                status.value = f'Stopped (debug)'
                steer()
                servo_pos(3)
                switch_lights(True)

                run = False

            if not switch.value and run and not objective.value == "debug":
                status.value = f'Stopped'
                steer()
                servo_pos(3)

                if objective.value == "zone":
                    time.sleep(2)
                    servo_pos(4)
                    time.sleep(.25)
                    servo_pos(6)

                    if not dumped_alive_victims:
                        picked_up_alive_count.value = 0
                    if not dumped_dead_victims:
                        picked_up_dead_count.value = 0

                switch_lights(True)

                objective.value = "follow_line"  # follow_line
                line_status.value = "line_detected"  # line_detected
                zone_status.value = "begin"  # begin

                run = False

            # debug switch reset
            if switch.value and not run and objective.value == "debug":
                gyro_x_offset(0)
                gyro_y_offset(0)
                gyro_z_offset(0)
                run = True

            # lop reset
            if switch.value and not run and not objective.value == "debug":

                # start timer
                if run_start_time.value == -1:
                    run_start_time.value = time.perf_counter()

                gyro_x_offset(0)
                gyro_y_offset(0)
                gyro_z_offset(0)

                servo_pos(5)
                time.sleep(.25)
                servo_pos(7)

                # reset all average time arrays
                time_last_angles = empty_time_arr()

                time_last_gyro_y = empty_time_arr()
                time_last_gyro_x = empty_time_arr()
                time_last_gyro_z = empty_time_arr()

                time_sensor_one = empty_time_arr()
                time_sensor_two = empty_time_arr()
                time_sensor_three = empty_time_arr()
                time_sensor_four = empty_time_arr()
                time_sensor_five = empty_time_arr()
                time_sensor_six = empty_time_arr()
                time_sensor_seven = empty_time_arr()

                time_line_similarity = fill_array(0, 1200)
                time_zone_similarity = fill_array(0.7, 1200)
                timer.set_timer("stuck_cooldown", 5)

                time.sleep(.25)

                run = True

            if run:
                if objective.value == "follow_line":

                    if seesaw_detected():
                        status.value = f'Avoiding seesaw'

                        avoid_seesaw()
                        time_last_gyro_y = fill_array(0)
                        time_sensor_one = fill_array(0)
                        time_sensor_two = fill_array(0)
                        time_sensor_five = fill_array(0)

                        timer.set_timer("obstacle_detect_cooldown", 1.5)
                        timer.set_timer("stuck_cooldown", 4)
                        continue

                    # detected line on last frame
                    if line_status.value == "line_detected":

                        if not line_detected.value and rotation_y.value == "none" and not ramp_ahead.value:
                            line_status.value = "gap_detected"

                        if red_detected.value:
                            line_status.value = "stop"

                        if obstacle_detected() or (obstacle_detected_again() and rotation_y.value == "ramp_up"):
                            line_status.value = "obstacle_detected"

                        if silver_detected():
                            if validate_silver():
                                if program_continue():
                                    if zone_start_time.value == -1:
                                        zone_start_time.value = time.perf_counter()

                                    line_status.value = "position_entry"
                            else:
                                steer(0, .7)
                                time.sleep(.3)
                                steer()
                                line_status.value = "line_detected"
                            timer.set_timer("silver_cooldown", 1.3)
                            timer.set_timer("stuck_cooldown", 6)
                            continue

                    # still line detected
                    if line_status.value == "line_detected":
                        if turn_dir.value == "turn_around":
                            status.value = f'Turning around {"right" if last_turn_dir == "r" else "left"}'

                            last_turn_dir = turn_around()
                            continue

                        status.value = f'Following Line'

                        steer(line_angle.value, get_speed(line_angle.value))

                        time_silver_detected = add_time_value(time_silver_detected, silver_value.value)
                        time_last_angles = add_time_value(time_last_angles, line_angle.value)

                        if get_time_average(time_line_similarity, 15) > .88 and timer.get_timer("stuck_cooldown"):
                            avoid_stuck()
                            timer.set_timer("stuck_cooldown", 4 if rotation_y.value == "none" else 8)


                    elif line_status.value == "stop":
                        stop_for_red()
                        line_status.value = "line_detected"
                        continue


                    elif line_status.value == "gap_detected":
                        verified_gap = orientate_gap()

                        if verified_gap:
                            timer.set_timer("gap_avoid", .4)
                        else:
                            line_status.value = "line_detected"
                            min_line_size.value = 3000
                            time.sleep(.1)

                        timer.set_timer("stuck_cooldown", 4)
                        continue


                    elif line_status.value == "gap_avoid":
                        status.value = f'Avoiding gap'

                        if line_detected.value or silver_detected() or obstacle_detected():
                            min_line_size.value = 3000
                            line_status.value = "line_detected"
                            timer.set_timer("stuck_cooldown", 4)
                            continue
                        else:
                            steer(0, .6)

                        if timer.get_timer("gap_avoid"):
                            min_line_size.value = 4500
                            steer(200, .6)
                            time.sleep(1.35)
                            drive_back_until_line(.3, .6)

                            line_status.value = "line_detected"
                            time.sleep(.1)
                            timer.set_timer("stuck_cooldown", 4)
                            continue


                    elif line_status.value == "obstacle_detected":
                        status.value = f'Obstacle detected'

                        start_angle = sensor_x.value
                        obstacle_is_ramp = rotation_y.value
                        if turn_for_obstacle():
                            line_status.value = "obstacle_avoid"

                            if rotation_y.value == "none":
                                timer.set_timer("obstacle_avoid", 1.6)
                            elif rotation_y.value == "ramp_up":
                                timer.set_timer("obstacle_avoid", 3.5)
                            elif rotation_y.value == "ramp_down":
                                timer.set_timer("obstacle_avoid", 1)

                            timer.set_timer("obstacke_cooldown", .45)

                            obstacle_direction.value = obstacle_dir[obstacle_count % len(obstacle_dir)]

                            time_line_similarity = fill_array(0, 1200)
                            min_line_size.value = 6500
                            time.sleep(.1)
                        else:
                            status.value = f'Obstacle failed, returning to {start_angle}°'
                            if program_continue():
                                return_after_failed_obstacle(start_angle)
                            line_status.value = "line_detected"
                        continue


                    elif line_status.value == "obstacle_avoid":
                        status.value = f'Avoiding obstacle'

                        if obstacle_dir[obstacle_count % len(obstacle_dir)] == "l" and not timer.get_timer("obstacle_avoid"):
                            if rotation_y.value == "none":
                                steer(max_turn_angle, .7)
                            elif rotation_y.value == "ramp_up":
                                steer(max_turn_angle - 40, 1)
                            elif rotation_y.value == "ramp_down":
                                steer(max_turn_angle, .3)

                        elif obstacle_dir[obstacle_count % len(obstacle_dir)] == "l" and timer.get_timer("obstacle_avoid") and not rotation_y.value == "ramp_up":
                            steer(180, .6)
                            time.sleep(.1)
                            if rotation_y.value == "none":
                                timer.set_timer("obstacle_avoid", .7)
                            elif rotation_y.value == "ramp_up":
                                timer.set_timer("obstacle_avoid", 1.9)
                            elif rotation_y.value == "ramp_down":
                                timer.set_timer("obstacle_avoid", .75)

                        elif obstacle_dir[obstacle_count % len(obstacle_dir)] == "r" and not timer.get_timer("obstacle_avoid"):
                            if rotation_y.value == "none":
                                steer(-max_turn_angle, .7)
                            elif rotation_y.value == "ramp_up":
                                steer(-max_turn_angle + 40, 1)
                            elif rotation_y.value == "ramp_down":
                                steer(-max_turn_angle, .3)

                        elif obstacle_dir[obstacle_count % len(obstacle_dir)] == "r" and timer.get_timer("obstacle_avoid") and not rotation_y.value == "ramp_up":
                            steer(-180, .6)
                            time.sleep(.1)
                            if rotation_y.value == "none":
                                timer.set_timer("obstacle_avoid", .7)
                            elif rotation_y.value == "ramp_up":
                                timer.set_timer("obstacle_avoid", 1.9)
                            elif rotation_y.value == "ramp_down":
                                timer.set_timer("obstacle_avoid", .75)

                        if get_time_average(time_line_similarity, 15) > .88 and timer.get_timer("stuck_cooldown"):
                            steer(180 if obstacle_dir[obstacle_count % len(obstacle_dir)] == "r" else -180, .7)
                            time.sleep(.4)
                            steer()
                            time.sleep(.2)
                            timer.set_timer("stuck_cooldown", 10)

                        if line_detected.value and timer.get_timer("obstacke_cooldown"):
                            min_line_size.value = 3000
                            line_status.value = "obstacle_orientate"

                            if obstacle_is_ramp == "none":
                                orientate_after_obstacle(obstacle_dir[obstacle_count % len(obstacle_dir)])

                                if line_detected.value:
                                    steer(200, .7)
                                    time.sleep(1)
                                    steer()
                            else:
                                steer(0, .3 if obstacle_is_ramp == "ramp_down" else .8)
                                time.sleep(.6 if obstacle_is_ramp == "ramp_down" else 1)
                                steer(180 if obstacle_dir[obstacle_count % len(obstacle_dir)] == "r" else -180, .7)
                                time.sleep(.3)

                            time_sensor_one = fill_array(300)
                            time_sensor_two = fill_array(300)
                            time_sensor_five = fill_array(300)

                            obstacle_count += 1
                            line_status.value = "line_detected"
                            timer.set_timer("stuck_cooldown", 4)
                            continue


                    elif line_status.value == "position_entry":
                        status.value = f'Positioning for entry'
                        if not speed_zone:
                            time.sleep(.5)
                        if rotation_y.value == "none":
                            if position_for_entry():
                                line_status.value = "line_detected"
                                objective.value = "zone"
                        else:
                            line_status.value = "line_detected"
                            objective.value = "zone"


                elif objective.value == "zone":

                    if zone_status.value == "begin":
                        if not wait_time(2 if speed_zone else 4, "AI model to load", rotation="u" if rotation_y.value == "ramp_up" else "n"):
                            continue

                        status.value = f'Driving into zone'

                        if rotation_y.value == "none":
                            gyro_x_offset(0)
                            gyro_y_offset(0)

                        if not speed_zone:
                            drive_until_wall(2.4 if rotation_y.value == "ramp_up" else .7)

                            avoid_angle = -361
                            if distance_left() < 200 or distance_right() < 200 and not (distance_left() < 200 and distance_right() < 200):
                                if distance_left() > distance_right():
                                    avoid_angle = add_angle(sensor_x.value, -90)
                                else:
                                    avoid_angle = add_angle(sensor_x.value, 90)

                            drive_until_wall(1.3)

                            if distance_left() < 200 or distance_right() < 200 and not (distance_left() < 200 and distance_right() < 200):
                                if distance_left() > distance_right():
                                    avoid_angle = add_angle(sensor_x.value, -90)
                                else:
                                    avoid_angle = add_angle(sensor_x.value, 90)

                            if avoid_angle != -361:
                                turn_to_angle(avoid_angle, tolerance=5)

                                reason, time_driven = drive_until_wall(1, stop_when_black=True, stop_when_silver=True, stop_when_victim=True, return_driven_time=True, speed=.9)

                                if reason in ["black", "silver"]:
                                    steer(200, .7)
                                    time.sleep(.3)
                                    turn_to_angle(add_angle(sensor_x.value, 180), tolerance=5, direction="r")

                                    drive_until_wall(time_driven + 1.8, stop_when_black=True, stop_when_silver=True)

                        else:
                            drive_until_wall(2 if rotation_y.value == "ramp_up" else 1, speed=1)

                        timer.set_timer("max_search_time", 240)
                        time_zone_similarity = fill_array(0.7, 1200)

                        if dumped_dead_victims:
                            zone_status.value = "deposit_red"
                        else:
                            zone_status.value = "find_balls"
                        continue


                    elif zone_status.value == "find_balls":
                        status.value = f'Searching for victims'

                        if ball_type.value == "none":
                            search_for_victims()
                            if timer.get_timer("max_search_time"):
                                zone_status.value = "deposit_green"
                                continue
                        else:
                            zone_status.value = "pickup_ball"
                            continue


                    elif zone_status.value == "pickup_ball":
                        time_victim_type = empty_time_arr(1200)

                        if turn_to_victim():
                            if drive_to_victim(speed=1 if speed_zone else .6):
                                victim_type = "silver ball" if get_time_average(time_victim_type, 10) > 0.5 else "black ball"
                                status.value = f"Picking up {'alive' if victim_type == 'silver ball' else 'dead'} victim"

                                alive = victim_type == "silver ball"
                                if not alive and picked_up_dead_count.value > 0:
                                    alive = True
                                elif alive and picked_up_alive_count.value > 1:
                                    alive = False

                                if pick_up_victim(alive):
                                    if alive and picked_up_alive_count.value < 2:
                                        picked_up_alive_count.value += 1
                                    else:
                                        picked_up_dead_count.value += 1

                                    status.value = f"Picked up {'alive' if alive else 'dead'} victim, new total: {picked_up_alive_count.value + picked_up_dead_count.value} victims"
                                    if not speed_zone:
                                        time.sleep(1)
                                else:
                                    status.value = f"Failed to pick up {'alive' if alive else 'dead'} victim"
                                    if not speed_zone:
                                        time.sleep(1)

                                if picked_up_alive_count.value + picked_up_dead_count.value == 3:
                                    zone_status.value = "deposit_green"
                                    continue

                        zone_status.value = "find_balls"
                        continue


                    elif zone_status.value == "deposit_green":
                        if not dumped_alive_victims:
                            status.value = f'Searching for green evacuation point'

                            search_for_corner()

                            if turn_to_corner("green"):
                                if drive_to_corner("green", speed=.75 if speed_zone else .6):
                                    if dump_victims(True):

                                        if speed_zone:
                                            dumped_alive_victims = True
                                        else:
                                            if wait_time(6, "confirmation of successful dump", rotation="n"):
                                                dumped_alive_victims = True

                                        time_zone_similarity = fill_array(0.7, 1200)
                                        zone_status.value = "deposit_red"
                        else:
                            servo_pos(6)
                            zone_status.value = "deposit_red"


                    elif zone_status.value == "deposit_red":
                        status.value = f'Searching for red evacuation point'

                        search_for_corner()

                        if turn_to_corner("red"):
                            if drive_to_corner("red", speed=.75 if speed_zone else .6):
                                if dump_victims(False, dumped_dead_victims):
                                    if not dumped_dead_victims:
                                        if speed_zone:
                                            dumped_dead_victims = True
                                        else:
                                            if wait_time(6, "confirmation of successful dump", rotation="n"):
                                                dumped_dead_victims = True
                                    time_zone_similarity = fill_array(0.7, 1200)
                                    zone_status.value = "exit"


                    elif zone_status.value == "exit":
                        status.value = f'Searching for exit'

                        if orientate_at_corner:
                            gyro_x_offset(45)

                        switch_lights(True)

                        if find_exit():
                            status.value = f'Found zone exit'
                            if not speed_zone:
                                time.sleep(1)

                                zone_status.value = "get_exit_angle"
                                position_exit()

                            else:
                                switch_lights(True)

                            zone_status.value = "exit"

                            if not speed_zone:
                                if not wait_time(6, "confirmation of exit position", rotation="n"):
                                    continue

                            timer.set_timer("obstacle_detect_cooldown", 3)

                            objective.value = "follow_line"
                            line_status.value = "line_detected"
                            zone_status.value = "begin"

                            zone_done = True
                            time_line_similarity = fill_array(0, 1200)

                            if speed_zone:
                                steer(0, .6)

                            time.sleep(.7)
                            steer()
                            time.sleep(1)

                            zone_start_time.value = -1

                            continue


                elif objective.value == "debug":
                    status.value = f'Debugging'

                    time.sleep(1)


        elif calibrate_color_status.value == "calibrate":
            if not calibration_switched_light:
                if calibration_color.value == "z-g" or calibration_color.value == "z-r" or calibration_color.value == "l-bz" or calibration_color.value == "l-bv":
                    switch_lights(False)
                else:
                    switch_lights(True)
                calibration_switched_light = True

        if time.perf_counter() - iteration_limit_time < 1 / max_iterations:
            time.sleep(abs(1 / max_iterations - (time.perf_counter() - iteration_limit_time)))
        iteration_limit_time = time.perf_counter()

        counter += 1
        if time.perf_counter() - iteration_time > 1:
            iterations_control.value = int(counter / (time.perf_counter() - iteration_time))
            iteration_time = time.perf_counter()
            counter = 0

    servo_pos(5)
    time.sleep(.25)
    servo_pos(7)
    time.sleep(.25)
    servo_pos(3)
