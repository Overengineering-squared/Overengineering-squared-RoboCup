import RPi.GPIO as GPIO

in1 = 23
in2 = 24
in3 = 27
in4 = 22
ena = 12
enb = 13

temp1 = 1
speed = 50
steering = 0
motorACorrection = 1
motorBCorrection = 1

GPIO.setmode(GPIO.BCM)
GPIO.setup(in1, GPIO.OUT)
GPIO.setup(in2, GPIO.OUT)
GPIO.setup(in3, GPIO.OUT)
GPIO.setup(in4, GPIO.OUT)
GPIO.setup(ena, GPIO.OUT)
GPIO.setup(enb, GPIO.OUT)
GPIO.output(in1, GPIO.LOW)
GPIO.output(in2, GPIO.LOW)
GPIO.output(in3, GPIO.LOW)
GPIO.output(in4, GPIO.LOW)

pa = GPIO.PWM(ena, 1000)
pa.start(speed * motorACorrection)

pb = GPIO.PWM(enb, 1000)
pb.start(speed * motorBCorrection)

print("\n")
print("The default speed & direction of motor is LOW & Forward.....")
print("r-run s-stop f-forward b-backward left right lt-left turn rt-right turn l-low m-medium h-high e-exit")
print("\n")
try:
    while (1):

        x = input()

        if x == 'r':
            print("run")
            if (temp1 == 1):
                pa.ChangeDutyCycle(0)
                pb.ChangeDutyCycle(0)
                GPIO.output(in1, GPIO.LOW)
                GPIO.output(in2, GPIO.HIGH)
                GPIO.output(in3, GPIO.LOW)
                GPIO.output(in4, GPIO.HIGH)
                pa.ChangeDutyCycle(speed * motorACorrection)
                pb.ChangeDutyCycle(speed * motorBCorrection)
                print("forward")
                steering = 0
                x = 'z'
            else:
                pa.ChangeDutyCycle(0)
                pb.ChangeDutyCycle(0)
                GPIO.output(in1, GPIO.HIGH)
                GPIO.output(in2, GPIO.LOW)
                GPIO.output(in3, GPIO.HIGH)
                GPIO.output(in4, GPIO.LOW)
                pa.ChangeDutyCycle(speed * motorACorrection)
                pb.ChangeDutyCycle(speed * motorBCorrection)
                print("backward")
                steering = 0
                x = 'z'


        elif x == 's':
            print("stop")
            GPIO.output(in1, GPIO.LOW)
            GPIO.output(in2, GPIO.LOW)
            GPIO.output(in3, GPIO.LOW)
            GPIO.output(in4, GPIO.LOW)
            pa.ChangeDutyCycle(0)
            pb.ChangeDutyCycle(0)
            steering = 0
            x = 'z'

        elif x == 'f':
            print("forward")
            pa.ChangeDutyCycle(0)
            pb.ChangeDutyCycle(0)
            GPIO.output(in1, GPIO.LOW)
            GPIO.output(in2, GPIO.HIGH)
            GPIO.output(in3, GPIO.LOW)
            GPIO.output(in4, GPIO.HIGH)
            pa.ChangeDutyCycle(speed * motorACorrection)
            pb.ChangeDutyCycle(speed * motorBCorrection)
            temp1 = 1
            steering = 0
            x = 'z'

        elif x == 'b':
            print("backward")
            pa.ChangeDutyCycle(0)
            pb.ChangeDutyCycle(0)
            GPIO.output(in1, GPIO.HIGH)
            GPIO.output(in2, GPIO.LOW)
            GPIO.output(in3, GPIO.HIGH)
            GPIO.output(in4, GPIO.LOW)
            pa.ChangeDutyCycle(speed * motorACorrection)
            pb.ChangeDutyCycle(speed * motorBCorrection)
            temp1 = 0
            steering = 0
            x = 'z'

        elif x == "right":
            if 0 <= steering < 1:
                steering = steering + .1
            else:
                steering = 0
            pa.ChangeDutyCycle(speed * (1 - steering) * motorACorrection)
            pb.ChangeDutyCycle(speed * motorBCorrection)
            print("right: " + str(steering))
            x = 'z'

        elif x == "left":
            if 0 >= steering > -1:
                steering = steering - .1
            else:
                steering = 0
            pa.ChangeDutyCycle(speed * motorACorrection)
            pb.ChangeDutyCycle(speed * (1 + steering) * motorBCorrection)

            print("left: " + str(steering))
            x = 'z'

        elif x == "lt":
            pa.ChangeDutyCycle(0)
            pb.ChangeDutyCycle(0)
            GPIO.output(in1, GPIO.HIGH)
            GPIO.output(in2, GPIO.LOW)
            GPIO.output(in3, GPIO.LOW)
            GPIO.output(in4, GPIO.HIGH)
            pa.ChangeDutyCycle(speed * motorACorrection)
            pb.ChangeDutyCycle(speed * motorBCorrection)

            print("left turn")
            x = 'z'

        elif x == "rt":
            pa.ChangeDutyCycle(0)
            pb.ChangeDutyCycle(0)
            GPIO.output(in1, GPIO.LOW)
            GPIO.output(in2, GPIO.HIGH)
            GPIO.output(in3, GPIO.HIGH)
            GPIO.output(in4, GPIO.LOW)
            pa.ChangeDutyCycle(speed * motorACorrection)
            pb.ChangeDutyCycle(speed * motorBCorrection)

            print("right turn")
            x = 'z'

        elif x == 'l':
            print("low")
            speed = 40
            pa.ChangeDutyCycle(speed * motorACorrection)
            pb.ChangeDutyCycle(speed * motorBCorrection)
            x = 'z'

        elif x == 'm':
            print("medium")
            speed = 60
            pa.ChangeDutyCycle(speed * motorACorrection)
            pb.ChangeDutyCycle(speed * motorBCorrection)
            x = 'z'

        elif x == 'h':
            print("high")
            speed = 75
            pa.ChangeDutyCycle(speed * motorACorrection)
            pb.ChangeDutyCycle(speed * motorBCorrection)
            x = 'z'


        elif x == 'e':
            break

        else:
            print("<<<  wrong data  >>>")
            print("please enter the defined data to continue.....")

except KeyboardInterrupt:
    print("KeyboardInterrupt")
finally:
    GPIO.cleanup()
