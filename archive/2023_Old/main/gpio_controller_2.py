from gpiozero import *

# program variables

# gpio pins
in_1 = 0  # forwards right
in_2 = 1  # backwards right
in_3 = 5  # forwards left
in_4 = 6  # backwards right
en_a = 12  # speed right
en_b = 13  # speed left

led = 20  # lighting pin
button_pin = 21

# corrections due to different motor speeds
left_correction = 1
right_correction = 1

# gpio setup
forward_right = LED(in_1)
backward_right = LED(in_2)
forward_left = LED(in_3)
backward_left = LED(in_4)

speed_right = PWMLED(en_a, frequency=1000)
speed_left = PWMLED(en_b, frequency=1000)
speed_right.value = 0.55
speed_left.value = 0.55

light = LED(led)
button = Button(button_pin)


def switch_lights(light_on):
    if light_on:
        light.on()
    else:
        light.off()


def steer(angle=190, speed=0.55):
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
            print(1)
            if angle > 150:
                forward_right.on()
                backward_right.off()
                forward_left.off()
                backward_left.on()
                speed_left.value = min(speed * left_correction * 1.3, 1)
                speed_right.value = min(speed * right_correction * 1.3, 1)
            else:
                print(speed_left.value)
                speed_left.value = min(speed * left_correction, 1)
                print(2)
                speed_right.value = min(speed * right_correction * ((150 - angle) / 149), 1)
                print(3)

        # left
        else:
            if angle < -150:
                forward_right.off()
                backward_right.on()
                forward_left.on()
                backward_left.off()
                speed_left.value = min(speed * left_correction * 1.3, 1)
                speed_right.value = min(speed * right_correction * 1.3, 1)
            else:
                speed_left.value = min(speed * left_correction * ((150 + angle) / 149), 1)
                speed_right.value = min(speed * right_correction, 1)

        print(4)
