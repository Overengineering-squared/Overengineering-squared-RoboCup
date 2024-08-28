import serial

from line import *

ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1, dsrdtr=True, rtscts=True)
ser.reset_input_buffer()

manager = multiprocessing.Manager()

sensor_one = manager.Value("i", -1.0)
sensor_two = manager.Value("i", -1.0)
sensor_three = manager.Value("i", -1.0)
sensor_x = manager.Value("i", 361.0)
sensor_y = manager.Value("i", 361.0)
x_offset = manager.Value("i", 0.0)
y_offset = manager.Value("i", 0.0)


def gyro_x_offset(angle):
    if not sensor_x.value == 361:
        x_offset.value = float(angle - (sensor_x.value - x_offset.value))


def gyro_y_offset(angle):
    if not sensor_y.value == 361:
        y_offset.value = float(angle - (sensor_y.value - y_offset.value))


def serial_loop():
    while True:
        if ser.in_waiting > 0:
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
                elif serial.startswith("GX "):
                    sensor_x.value = round((float(serial.split(" ")[1]) + x_offset.value) % 360, 2)
                elif serial.startswith("GY "):
                    sensor_y.value = round(float(serial.split(" ")[1]) + y_offset.value, 2)
