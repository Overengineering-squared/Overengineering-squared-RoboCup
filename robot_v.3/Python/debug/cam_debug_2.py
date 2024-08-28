import time

import cv2
from picamera2 import Picamera2


def main():
    # Open the video capture
    camera = Picamera2(1)
    camera.start()

    # Initialize the FPS counter variables
    fps_start_time = time.time()
    fps_frames_count = 0

    while True:
        # Read a frame from the video capture
        frame = camera.capture_array()
        image = cv2.cvtColor(frame, cv2.COLOR_RGBA2BGR)

        # Display the frame
        cv2.imshow("Video", image)

        # Update the FPS counter
        fps_frames_count += 1
        if time.time() - fps_start_time >= 1:
            fps = fps_frames_count / (time.time() - fps_start_time)
            print("FPS:", fps)
            fps_start_time = time.time()
            fps_frames_count = 0

        # Exit the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        time.sleep(0.01)

    # Release the video capture and close the OpenCV windows
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
