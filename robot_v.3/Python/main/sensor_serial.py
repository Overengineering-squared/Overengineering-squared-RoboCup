import serial

from mp_manager import *

serial_port = serial.Serial('/dev/ttyUSB0', 115200, timeout=1, dsrdtr=True, rtscts=True)
serial_port.reset_input_buffer()


def serial_loop():
    time.sleep(.2)

    iteration_limit_time = time.perf_counter()
    max_iterations = 60
    iteration_time = time.perf_counter()
    counter = 0

    while not terminate.value:
        if serial_port.in_waiting > 0:
            try:
                line = serial_port.readline().decode().rstrip()
            except UnicodeDecodeError or UnboundLocalError:
                print("UnicodeDecodeError or UnboundLocalError")
                continue

            try:
                if line.startswith("S1 "):
                    data = line.split(" ")[1]
                    if data == "No":
                        sensor_one.value = -2.0
                    elif data == "-1":
                        sensor_one.value = 1400.0
                    else:
                        sensor_one.value = float(data)
                elif line.startswith("S2 "):
                    data = line.split(" ")[1]
                    if data == "No":
                        sensor_two.value = -2.0
                    elif data == "-1":
                        sensor_two.value = 1400.0
                    else:
                        sensor_two.value = float(data)
                elif line.startswith("S3 "):
                    data = line.split(" ")[1]
                    if data == "No":
                        sensor_three.value = -2.0
                    elif data == "-1":
                        sensor_three.value = 1400.0
                    else:
                        sensor_three.value = float(data)
                elif line.startswith("S4 "):
                    data = line.split(" ")[1]
                    if data == "No":
                        sensor_four.value = -2.0
                    elif data == "-1":
                        sensor_four.value = 1400.0
                    else:
                        sensor_four.value = float(data)
                elif line.startswith("S5 "):
                    data = line.split(" ")[1]
                    if data == "No":
                        sensor_five.value = -2.0
                    elif data == "-1":
                        sensor_five.value = 1400.0
                    else:
                        sensor_five.value = float(data)
                elif line.startswith("S6 "):
                    data = line.split(" ")[1]
                    if data == "No":
                        sensor_six.value = -2.0
                    elif data == "-1":
                        sensor_six.value = 1400.0
                    else:
                        sensor_six.value = float(data)
                elif line.startswith("S7 "):
                    data = line.split(" ")[1]
                    if data == "No":
                        sensor_seven.value = -2.0
                    elif data == "-1":
                        sensor_seven.value = 1400.0
                    else:
                        sensor_seven.value = float(data)
                elif line.startswith("G1 "):
                    data = line.split(" ")[2]
                    if data == "No":
                        sensor_x_1.value = 361.0
                        print("G1: X: No data")
                    else:
                        sensor_x_1.value = round(float(data), 2)

                    data = line.split(" ")[4]
                    if data == "No":
                        sensor_y_1.value = 361.0
                        print("G1: Y: No data")
                    else:
                        sensor_y_1.value = round(float(data), 2)

                    data = line.split(" ")[6]
                    if data == "No":
                        sensor_z_1.value = 361.0
                        print("G1: Z: No data")
                    else:
                        sensor_z_1.value = round(float(data), 2)

                    data = line.split(" ")[8]
                    if data == "No":
                        sensor_ax_1.value = 361.0
                    else:
                        sensor_ax_1.value = float(data)

                    data = line.split(" ")[10]
                    if data == "No":
                        sensor_ay_1.value = 361.0
                    else:
                        sensor_ay_1.value = float(data)

                    average_rotation()

                elif line.startswith("G2 "):
                    data = line.split(" ")[2]
                    if data == "No":
                        sensor_x_2.value = 361.0
                        print("G2: X: No data")
                    else:
                        sensor_x_2.value = round(float(data), 2)

                    data = line.split(" ")[4]
                    if data == "No":
                        sensor_y_2.value = 361.0
                        print("G2: Y: No data")
                    else:
                        sensor_y_2.value = round(float(data), 2)

                    data = line.split(" ")[6]
                    if data == "No":
                        sensor_z_2.value = 361.0
                        print("G2: Z: No data")
                    else:
                        sensor_z_2.value = round(float(data), 2)

                    data = line.split(" ")[8]
                    if data == "No":
                        sensor_ax_2.value = 361.0
                    else:
                        sensor_ax_2.value = float(data)

                    data = line.split(" ")[10]
                    if data == "No":
                        sensor_ay_2.value = 361.0
                    else:
                        sensor_ay_2.value = float(data)

                    average_rotation()

            except ValueError or IndexError:
                print("ValueError or IndexError")

        if time.perf_counter() - iteration_limit_time < 1 / max_iterations:
            time.sleep(abs(1 / max_iterations - (time.perf_counter() - iteration_limit_time)))
        iteration_limit_time = time.perf_counter()

        counter += 1
        if time.perf_counter() - iteration_time > 1:
            iterations_serial.value = int(counter / (time.perf_counter() - iteration_time))
            iteration_time = time.perf_counter()
            counter = 0
