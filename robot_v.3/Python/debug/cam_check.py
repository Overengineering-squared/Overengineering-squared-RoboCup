import sys
import time

import cv2


def main():
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error opening camera")
        sys.exit()

    start_time = time.time()

    while True:
        ret, frame = cap.read()

        if not ret:
            print("Can't receive frame. Exiting ...")
            break

        cv2.imshow('Video', frame)

        if time.time() - start_time > 1:
            print("Camera working")
            break

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
