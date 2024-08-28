import time
from multiprocessing import Manager

import numpy as np

from Managers import ConfigManager

config_manager = ConfigManager('config.ini')

manager = Manager()

terminate = manager.Value("i", False)

sensor_one = manager.Value("i", -2.0)  # Front Left
sensor_two = manager.Value("i", -2.0)  # Front Right
sensor_three = manager.Value("i", -2.0)  # Left
sensor_four = manager.Value("i", -2.0)  # Right
sensor_five = manager.Value("i", -2.0)  # Front Center
sensor_six = manager.Value("i", -2.0)  # Back
sensor_seven = manager.Value("i", -2.0)  # Gripper

sensor_x_1 = manager.Value("i", 361.0)
sensor_x_2 = manager.Value("i", 361.0)
sensor_y_1 = manager.Value("i", 361.0)
sensor_y_2 = manager.Value("i", 361.0)
sensor_z_1 = manager.Value("i", 361.0)
sensor_z_2 = manager.Value("i", 361.0)
sensor_ax_1 = manager.Value("i", 361.0)
sensor_ax_2 = manager.Value("i", 361.0)
sensor_ay_1 = manager.Value("i", 361.0)
sensor_ay_2 = manager.Value("i", 361.0)

sensor_x = manager.Value("i", 361.0)
sensor_y = manager.Value("i", 361.0)
sensor_z = manager.Value("i", 361.0)

x_offset_1 = manager.Value("i", 0.0)
x_offset_2 = manager.Value("i", 0.0)
y_offset_1 = manager.Value("i", 0.0)
y_offset_2 = manager.Value("i", 0.0)
z_offset_1 = manager.Value("i", 0.0)
z_offset_2 = manager.Value("i", 0.0)
x_acc_mean = manager.Value("i", 0.0)

rotation_y = manager.Value("i", "none")  # "ramp_up""; "ramp_down"; "none"

obstacle_direction = manager.Value("i", "n")
min_line_size = manager.Value("i", 3000)

line_angle = manager.Value("i", 0.)
line_angle_y = manager.Value("i", -1)
line_detected = manager.Value("i", False)
line_crop = manager.Value("i", .6)
line_similarity = manager.Value("i", 0.)
gap_angle = manager.Value("i", 0.)
gap_center_x = manager.Value("i", -180)
gap_center_y = manager.Value("i", -1)
silver_angle = manager.Value("i", -181)
line_size = manager.Value("i", 0.)
ramp_ahead = manager.Value("i", False)
red_detected = manager.Value("i", False)
turn_dir = manager.Value("i", "straight")  # "straight"; "left"; "right"; "turn_around"
silver_value = manager.Value("i", -1.)
black_average = manager.Value("i", 0.)

ball_distance = manager.Value("i", 0)
ball_type = manager.Value("i", "none")  # "none"; "black ball"; "silver ball"
ball_width = manager.Value("i", -1)
zone_similarity = manager.Value("i", 0.)
zone_similarity_average = manager.Value("i", 0.)
zone_found_black = manager.Value("i", False)
zone_found_green = manager.Value("i", False)
zone_found_red = manager.Value("i", False)
exit_angle = manager.Value("i", -181.)
corner_distance = manager.Value("i", -181)
corner_size = manager.Value("i", 0)

picked_up_alive_count = manager.Value("i", 0)
picked_up_dead_count = manager.Value("i", 0)

switch = manager.Value("i", False)
program_start_time = manager.Value("i", -1)
run_start_time = manager.Value("i", -1)
zone_start_time = manager.Value("i", -1)

capture_image = manager.Value("i", False)
calibrate_color_status = manager.Value("i", "none")  # "none"; "calibrate"; "check"
calibration_color = manager.Value("i", "z-g")  # "z-g"; "z-r"; "l-gz"; "l-rz"; "l-bz; "l-bn"; "l-bv"; "l-bvl"; "l-bd"; "l-gl"; "l-rl"
iterations_control = manager.Value("i", -1)
iterations_serial = manager.Value("i", -1)
sensor1_disconnected = manager.Value("i", False)
sensor2_disconnected = manager.Value("i", False)

objective = manager.Value("i", "follow_line")  # "follow_line"; "zone"; "debug"
line_status = manager.Value("i", "line_detected")  # "line_detected"; "gap_detected"; "gap_avoid"; "obstacle_detected"; "obstacle_avoid"; "obstacle_orientate"; "check_silver"; "position_entry"; "position_entry_1"; "position_entry_2"; "stop"
zone_status = manager.Value("i", "begin")  # "begin"; "find_balls"; "pickup_ball"; "deposit_red"; "deposit_green"; "exit"

status = manager.Value("i", "Stopped")


def average_rotation():
    if (time.perf_counter() - program_start_time.value) > 7 and not program_start_time.value == -1:
        if not sensor1_disconnected.value:
            sensor1_disconnected.value = sensor_x_1.value == 0 and sensor_y_1.value == 0 and sensor_z_1.value == 0 and sensor_ax_1.value == 0 and sensor_ay_1.value == 0
            if sensor1_disconnected.value:
                print("Sensor 1 disconnected")

        if not sensor2_disconnected.value:
            sensor2_disconnected.value = sensor_x_2.value == 0 and sensor_y_2.value == 0 and sensor_z_2.value == 0 and sensor_ax_2.value == 0 and sensor_ay_2.value == 0
            if sensor2_disconnected.value:
                print("Sensor 2 disconnected")

    gyro_x_1 = (sensor_x_1.value + x_offset_1.value) % 360
    gyro_x_2 = (sensor_x_2.value + x_offset_2.value) % 360

    if abs(gyro_x_1 - gyro_x_2) > 180:
        if gyro_x_1 < gyro_x_2:
            gyro_x_1 += 360
        else:
            gyro_x_2 += 360

    if not sensor_x_1.value == 361 and not sensor_x_2.value == 361 and not sensor1_disconnected.value and not sensor2_disconnected.value:
        sensor_x.value = round(((gyro_x_1 + gyro_x_2) / 2) % 360, 2)
    elif sensor_x_1.value == 361 or sensor1_disconnected.value:
        sensor_x.value = round((sensor_x_2.value + x_offset_2.value) % 360, 2)
    elif sensor_x_2.value == 361 or sensor2_disconnected.value:
        sensor_x.value = round((sensor_x_1.value + x_offset_1.value) % 360, 2)

    if not sensor_y_1.value == 361 and not sensor_y_2.value == 361 and not sensor1_disconnected.value and not sensor2_disconnected.value:
        sensor_y.value = -round(((sensor_y_1.value + y_offset_1.value) - (sensor_y_2.value + y_offset_2.value)) / 2, 2)
    elif sensor_y_1.value == 361 or sensor1_disconnected.value:
        sensor_y.value = round((sensor_y_2.value + y_offset_2.value), 2)
    elif sensor_y_2.value == 361 or sensor2_disconnected.value:
        sensor_y.value = -round((sensor_y_1.value + y_offset_1.value), 2)

    if not sensor_z_1.value == 361 and not sensor_z_2.value == 361 and not sensor1_disconnected.value and not sensor2_disconnected.value:
        sensor_z.value = round(((sensor_z_1.value + z_offset_1.value) - (sensor_z_2.value + z_offset_2.value)) / 2, 2)
    elif sensor_z_1.value == 361 or sensor1_disconnected.value:
        sensor_z.value = round((sensor_z_2.value + z_offset_2.value), 2)
    elif sensor_z_2.value == 361 or sensor2_disconnected.value:
        sensor_z.value = round((sensor_z_1.value + z_offset_1.value), 2)


def empty_time_arr(length: int = 240):
    return np.zeros((length, 2))


def fill_array(value: int, length: int = 240, fill_time: int = 0):
    arr = np.zeros((length, 2))
    arr[fill_time:, 0] = time.perf_counter()
    arr[:, 1] = value
    return arr


def add_time_value(time_value_array, value):
    return np.delete(np.vstack((time_value_array, [time.perf_counter(), value])), 0, axis=0)


def get_time_average(time_value_array, time_range):
    time_value_array = time_value_array[np.where(time_value_array[:, 0] > time.perf_counter() - time_range)]
    if time_value_array.size > 0:
        return np.mean(time_value_array[:, 1])
    else:
        return -1


def get_max_value(time_value_array, time_range):
    time_value_array = time_value_array[np.where(time_value_array[:, 0] > time.perf_counter() - time_range)]
    return np.max(time_value_array[:, 1])


def calculate_x_offset(current_angle, target_angle):
    offset = target_angle - current_angle
    if offset > 180:
        offset -= 360
    elif offset < -180:
        offset += 360
    return offset


def gyro_x_offset(target_angle):
    sensor1_disconnected.value = False
    sensor2_disconnected.value = False

    current_angle_x_1 = sensor_x_1.value
    current_angle_x_2 = sensor_x_2.value

    if not sensor_x_1.value == 361:
        x_offset_1.value = float(calculate_x_offset(current_angle_x_1, target_angle))

    if not sensor_x_2.value == 361:
        x_offset_2.value = float(calculate_x_offset(current_angle_x_2, target_angle))


def gyro_y_offset(angle):
    if not sensor_y_1.value == 361:
        y_offset_1.value = float(angle - sensor_y_1.value)

    if not sensor_y_2.value == 361:
        y_offset_2.value = float(angle - sensor_y_2.value)


def gyro_z_offset(angle):
    if not sensor_z_1.value == 361:
        z_offset_1.value = float(angle - sensor_z_1.value)

    if not sensor_z_2.value == 361:
        z_offset_2.value = float(angle - sensor_z_2.value)


def find_average_color(image):
    avg_color_per_row = np.average(image, axis=0)
    avg_color = np.average(avg_color_per_row, axis=0)
    return avg_color
