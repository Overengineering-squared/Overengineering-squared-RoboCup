import RPi.GPIO as GPIO

# motor setup
in1 = 27  # forwards right
in2 = 22  # backwards right
in3 = 23  # forwards left
in4 = 24  # backwards right
ena = 17  # speed right
enb = 18  # speed left

# GPIO setup 
GPIO.setmode(GPIO.BCM)
GPIO.setup(in1, GPIO.OUT)
GPIO.setup(in2, GPIO.OUT)
GPIO.setup(in3, GPIO.OUT)
GPIO.setup(in4, GPIO.OUT)
GPIO.setup(ena, GPIO.OUT)
GPIO.setup(enb, GPIO.OUT)

# PWM setup
speedR = GPIO.PWM(ena, 1000)
speedR.start(0)
speedL = GPIO.PWM(enb, 1000)
speedL.start(0)

# motor corrections due to different motor speeds
motorACorrection = 1
motorBCorrection = 1


# cleanup GPIO-Pin after termination
def GPIO_reset():
    GPIO.cleanup()


# driving method
def steer(angle=190, speed=55):
    # stop
    if angle == 190:
        GPIO.output(in1, GPIO.LOW)
        GPIO.output(in2, GPIO.LOW)
        GPIO.output(in3, GPIO.LOW)
        GPIO.output(in4, GPIO.LOW)
        speedL.ChangeDutyCycle(0)
        speedR.ChangeDutyCycle(0)
        return

    # backward
    elif angle == 200:
        GPIO.output(in1, GPIO.HIGH)
        GPIO.output(in2, GPIO.LOW)
        GPIO.output(in3, GPIO.HIGH)
        GPIO.output(in4, GPIO.LOW)
        speedL.ChangeDutyCycle(max(speed * motorACorrection, 0))
        speedR.ChangeDutyCycle(max(speed * motorBCorrection, 0))

    # steer foreward
    elif angle in range(-180, 181):
        GPIO.output(in1, GPIO.LOW)
        GPIO.output(in2, GPIO.HIGH)
        GPIO.output(in3, GPIO.LOW)
        GPIO.output(in4, GPIO.HIGH)

        # right
        if angle >= 0:
            if angle > 150:
                GPIO.output(in1, GPIO.HIGH)
                GPIO.output(in2, GPIO.LOW)
                GPIO.output(in3, GPIO.LOW)
                GPIO.output(in4, GPIO.HIGH)
                speedL.ChangeDutyCycle(min(speed * motorBCorrection, 100))
                speedR.ChangeDutyCycle(min((speed * motorACorrection) * ((angle - 150) / 30), 100))
            else:
                speedL.ChangeDutyCycle(min(speed * motorBCorrection, 100))
                speedR.ChangeDutyCycle(min((speed * motorBCorrection) * ((150 - angle) / 149), 100))
            return

        # left
        elif angle <= 0:
            if abs(angle) > 150:
                GPIO.output(in1, GPIO.LOW)
                GPIO.output(in2, GPIO.HIGH)
                GPIO.output(in3, GPIO.HIGH)
                GPIO.output(in4, GPIO.LOW)
                speedL.ChangeDutyCycle(min((speed * motorACorrection) * ((abs(angle) - 150) / 30), 100))
                speedR.ChangeDutyCycle(min(speed * motorBCorrection, 100))
            else:
                speedL.ChangeDutyCycle(min((speed * motorBCorrection) * ((150 - abs(angle)) / 149), 100))
                speedR.ChangeDutyCycle(min(speed * motorBCorrection, 100))
            return

        # straight
        else:
            speedL.ChangeDutyCycle(min(speed * motorACorrection, 100))
            speedR.ChangeDutyCycle(min(speed * motorBCorrection, 100))
            return
