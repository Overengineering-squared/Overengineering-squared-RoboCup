import time

import cv2
import numpy as np

from Bluetooth import Bluetooth


def main():
    ev3 = Bluetooth()
    frame = np.zeros((200, 200, 3), dtype=np.uint8)

    while True:
        message = ev3.receive_message()

        if message is not None:
            print(message)
        else:
            time.sleep(0.1)

        cv2.imshow('frame', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


if __name__ == '__main__':
    main()
