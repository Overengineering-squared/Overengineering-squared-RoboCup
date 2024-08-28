import serial

from cam import *

ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1, dsrdtr=True, rtscts=True)
ser.reset_input_buffer()

manager = multiprocessing.Manager()

sensor_one = manager.Value("i", -1.0)
sensor_two = manager.Value("i", -1.0)
sensor_three = manager.Value("i", -1.0)
sensor_four = manager.Value("i", -1.0)
sensor_five = manager.Value("i", -1.0)
sensor_x = manager.Value("i", 361.0)
sensor_y = manager.Value("i", 361.0)
sensor_ax = manager.Value("i", 255.0)
sensor_ay = manager.Value("i", 255.0)
x_offset = manager.Value("i", 0.0)
y_offset = manager.Value("i", 0.0)
x_acc_mean = manager.Value("i", 0.0)

start_time = manager.Value("i", -1)
run_time = manager.Value("i", -1)


def gyro_x_offset(angle):
    if not sensor_x.value == 361:
        x_offset.value = float(angle - (sensor_x.value - x_offset.value))


def gyro_y_offset(angle):
    if not sensor_y.value == 361:
        y_offset.value = float(angle - (sensor_y.value - y_offset.value))


def serial_loop():
    time.sleep(.25)
    x_acc = np.zeros([11])

    while not terminate.value:
        if ser.in_waiting > 0:
            if not start_time.value == -1:
                run_time.value = round(float(time.perf_counter()) - start_time.value, 3)

            try:
                serial = ser.readline().decode('utf-8').rstrip()
            except UnicodeDecodeError or UnboundLocalError:
                terminate.value = True

            if len(serial.split(" ")) == 2:
                if serial.startswith("S1 "):
                    sensor_one.value = float(serial.split(" ")[1])
                elif serial.startswith("S2 "):
                    sensor_two.value = float(serial.split(" ")[1])
                elif serial.startswith("S3 "):
                    sensor_three.value = float(serial.split(" ")[1])
                elif serial.startswith("S4 "):
                    sensor_four.value = float(serial.split(" ")[1])
                elif serial.startswith("S5 "):
                    sensor_five.value = float(serial.split(" ")[1])
                elif serial.startswith("GX "):
                    new_x = round((float(serial.split(" ")[1]) + x_offset.value) % 360, 2)
                    x_acc = np.delete(np.append(x_acc, (((sensor_x.value - new_x) + 180) % 360) - 180), 0)
                    x_acc_mean.value = np.mean(x_acc)
                    sensor_x.value = new_x
                elif serial.startswith("GY "):
                    sensor_y.value = round(float(serial.split(" ")[1]) + y_offset.value, 2)
                elif serial.startswith("AX "):
                    sensor_ax.value = float(serial.split(" ")[1])
                elif serial.startswith("AY "):
                    sensor_ay.value = float(serial.split(" ")[1])
