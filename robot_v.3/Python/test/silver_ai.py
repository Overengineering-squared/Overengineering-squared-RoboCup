import time

import cv2
import numpy as np
from libcamera import controls
from picamera2 import Picamera2
from ultralytics import YOLO


def main():
    camera_x = 448
    camera_y = 252

    text_pos = np.array([int(camera_x * 0.96), int(camera_y * 0.04)])

    camera = Picamera2()
    mode = camera.sensor_modes[0]
    camera.configure(camera.create_video_configuration(sensor={'output_size': mode['size'], 'bit_depth': mode['bit_depth']}))
    camera.start()
    camera.set_controls({"AfMode": controls.AfModeEnum.Manual, "LensPosition": 6.5, "FrameDurationLimits": (1000000 // 30, 1000000 // 30)})  # ({"AfMode": controls.AfModeEnum.Manual, "LensPosition": 6.5, "FrameDurationLimits": (1000000 // 60, 1000000 // 60)})  {"AfMode": controls.AfModeEnum.Manual, "LensPosition": 0.4} {"AfMode": controls.AfModeEnum.Continuous, "AfSpeed": controls.AfSpeedEnum.Fast}

    model = YOLO('../../Ai/models/silver_zone_entry/silver_classify_s.onnx', task='classify')

    fps_time = time.perf_counter()
    counter = 0
    fps = 0

    fps_limit = 1 / 30
    fps_limit_time = time.perf_counter()

    while True:
        if time.perf_counter() - fps_limit_time <= fps_limit:
            continue

        fps_limit_time = time.perf_counter()

        frame = camera.capture_array()
        frame = cv2.resize(frame, (camera_x, camera_y))

        results = model.predict(frame, imgsz=(128, 96), conf=0.4, workers=4, verbose=True)

        annotated_frame = results[0].plot()

        counter += 1
        if time.perf_counter() - fps_time > 1:
            fps = int(counter / (time.perf_counter() - fps_time))
            fps_time = time.perf_counter()
            counter = 0

        cv2.putText(annotated_frame, str(fps), text_pos, cv2.FONT_HERSHEY_DUPLEX, .7, (0, 255, 0), 1, cv2.LINE_AA)

        cv2.imshow('Frame', annotated_frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
