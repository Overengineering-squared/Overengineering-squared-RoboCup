from Bluetooth import Bluetooth
from mp_manager import *


def bt_loop():
    ev3 = Bluetooth(debug=False)

    while True:
        message = ev3.receive_message()

        if message is not None:
            print('Received: ', message)

        if message in ["none", "left", "right"]:
            if message == "none":
                four_green_turn_dir.value = "straight"
            else:
                four_green_turn_dir.value = message
        elif message == "ramp":
            ramp_dropped.value = True
        else:
            time.sleep(0.1)
