import multiprocessing
import time

import RPi.GPIO as GPIO
import psutil

manager = multiprocessing.Manager()
cpu = manager.Value("i", 0.0)
switch = manager.Value("i", 0)

GPIO.setmode(GPIO.BCM)
pushpin = 21
GPIO.setup(pushpin, GPIO.IN, pull_up_down=GPIO.PUD_UP)


def sysinfo_loop():
    while True:
        time.sleep(1)
        cpu.value = psutil.cpu_percent(interval=1)
        switch.value = abs(GPIO.input(pushpin) - 1)
