import time

import numpy as np

from sensor_serial import *

samples = 100
distances = np.array([100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300])

if __name__ == "__main__":
    processes = []
    processes.append(multiprocessing.Process(target=serial_loop, args=()))

    for process in processes:
        process.start()
        print(process)
        time.sleep(0.5)

    for distance in distances:
        print(str(distance) + "mm: ")
        time.sleep(3)
        print("measuring")
        sensor1 = np.array([0])
        sensor2 = np.array([0])
        sensor3 = np.array([0])
        for i in range(samples):
            time.sleep(.1)
            sensor1 = np.append(sensor1, distance - sensor_one.value)
            sensor2 = np.append(sensor2, distance - sensor_two.value)
            sensor3 = np.append(sensor3, distance - sensor_three.value)
        print("sensor 1: " + str(np.mean(sensor1)) + "mm")
        print("sensor 2: " + str(np.mean(sensor2)) + "mm")
        print("sensor 3: " + str(np.mean(sensor3)) + "mm")

    for process in processes:
        process.terminate()
