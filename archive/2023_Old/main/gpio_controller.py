import RPi.GPIO as GPIO

# motor setup
in_1 = 0  # forwards right
in_2 = 1  # backwards right
in_3 = 5  # forwards left
in_4 = 6  # backwards right
en_a = 12  # speed right
en_b = 13  # speed left

led = 20  # led pin

# GPIO setup 
GPIO.setmode(GPIO.BCM)
GPIO.setup(in_1, GPIO.OUT)
GPIO.setup(in_2, GPIO.OUT)
GPIO.setup(in_3, GPIO.OUT)
GPIO.setup(in_4, GPIO.OUT)
GPIO.setup(en_a, GPIO.OUT)
GPIO.setup(en_b, GPIO.OUT)

GPIO.setup(led, GPIO.OUT)
GPIO.output(led, GPIO.LOW)

# PWM setup
speed_r = GPIO.PWM(en_a, 1000)
speed_r.start(55)
speed_l = GPIO.PWM(en_b, 1000)
speed_l.start(55)

# motor corrections due to different motor speeds
motor_a_Correction = 1
motor_b_Correction = 1


# cleanup GPIO-Pin after termination
def GPIO_reset():
    GPIO.cleanup()


def switch_lights(light_on):
    if light_on:
        GPIO.output(led, GPIO.LOW)
    else:
        GPIO.output(led, GPIO.HIGH)


# driving method
def steer(angle=190, speed=55):
    # stop
    if angle == 190:
        GPIO.output(in_1, GPIO.LOW)
        GPIO.output(in_2, GPIO.LOW)
        GPIO.output(in_3, GPIO.LOW)
        GPIO.output(in_4, GPIO.LOW)
        speed_l.ChangeDutyCycle(0)
        speed_r.ChangeDutyCycle(0)

        # backward
    elif angle == 200:
        GPIO.output(in_1, GPIO.HIGH)
        GPIO.output(in_2, GPIO.LOW)
        GPIO.output(in_3, GPIO.HIGH)
        GPIO.output(in_4, GPIO.LOW)
        speed_l.ChangeDutyCycle(max(speed * motor_a_Correction, 0))
        speed_r.ChangeDutyCycle(max(speed * motor_b_Correction, 0))

    # steer foreward
    elif angle in range(-180, 181):
        GPIO.output(in_1, GPIO.LOW)
        GPIO.output(in_2, GPIO.HIGH)
        GPIO.output(in_3, GPIO.LOW)
        GPIO.output(in_4, GPIO.HIGH)

        # right
        if angle >= 0:
            if angle > 150:
                GPIO.output(in_1, GPIO.HIGH)
                GPIO.output(in_2, GPIO.LOW)
                GPIO.output(in_3, GPIO.LOW)
                GPIO.output(in_4, GPIO.HIGH)
                speed_l.ChangeDutyCycle(min(speed * motor_a_Correction * 1.3, 100))
                speed_r.ChangeDutyCycle(min((speed * motor_b_Correction) * 1.3, 100))
                # speed_r.ChangeDutyCycle(min((speed * motor_b_Correction) * ((angle - 150) / 30), 100))
            else:
                speed_l.ChangeDutyCycle(min(speed * motor_a_Correction, 100))
                speed_r.ChangeDutyCycle(min((speed * motor_b_Correction) * ((150 - angle) / 149), 100))

        # left
        elif angle <= 0:
            if abs(angle) > 150:
                GPIO.output(in_1, GPIO.LOW)
                GPIO.output(in_2, GPIO.HIGH)
                GPIO.output(in_3, GPIO.HIGH)
                GPIO.output(in_4, GPIO.LOW)
                # speed_l.ChangeDutyCycle(min((speed * motor_a_Correction) * ((abs(angle) - 150) / 30), 100))
                speed_l.ChangeDutyCycle(min((speed * motor_a_Correction) * 1.3, 100))
                speed_r.ChangeDutyCycle(min((speed * motor_b_Correction) * 1.3, 100))
            else:
                speed_l.ChangeDutyCycle(min((speed * motor_a_Correction) * ((150 - abs(angle)) / 149), 100))
                speed_r.ChangeDutyCycle(min(speed * motor_b_Correction, 100))
