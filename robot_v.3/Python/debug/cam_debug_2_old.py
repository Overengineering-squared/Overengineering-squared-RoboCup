import time

import cv2


def main():
    # Open the video capture
    cap = cv2.VideoCapture(0)  # Use 0 for the first camera, 1 for the second, and so on
    print(cap.isOpened())
    time.sleep(5)
    # Check if the video capture is successfully opened
    if not cap.isOpened():
        print("Failed to open video capture")
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    # Initialize the FPS counter variables
    fps_start_time = time.time()
    fps_frames_count = 0

    while True:
        # Read a frame from the video capture
        ret, frame = cap.read()
        time.sleep(0.01)

        while ret == False:
            print("Can't receive frame. Retrying ...")
            cap.release()
            cap = cv2.VideoCapture(0)
            time.sleep(1)
            ret, frame = cap.read()

        # Display the frame
        cv2.imshow("Video", frame)

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
    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
