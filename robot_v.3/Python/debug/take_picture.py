import argparse
import os
import time

import cv2
from libcamera import controls
from picamera2 import Picamera2
from ultralytics import YOLO

from Timer import Timer

# Disable libcamera and Picamera2 logging
Picamera2.set_logging(Picamera2.ERROR)
os.environ["LIBCAMERA_LOG_LEVELS"] = "4"


def save_image(image, line: bool):
    path = "../../Ai/datasets/images_to_annotate/Line" if line else "../../Ai/datasets/images_to_annotate/Silver"
    if not os.path.exists(path):
        os.mkdir(path)
    num = len(os.listdir(path))
    cv2.imwrite(f"{path}/{num:04d}.png", image)


def main(line: bool, silver: bool):
    timer = Timer()

    # model = YOLO('../../Ai/models/silver_zone_entry/silver_classify_s.onnx', task='classify') # old model
    model = YOLO('../../Ai/models/test/silver_zone_entry/silver_classify_s.onnx', task='classify')

    camera_x = 448
    camera_y = 252

    camera = Picamera2()
    mode = camera.sensor_modes[0]
    camera.configure(camera.create_video_configuration(sensor={'output_size': mode['size'], 'bit_depth': mode['bit_depth']}))
    camera.start()
    camera.set_controls({"AfMode": controls.AfModeEnum.Manual, "LensPosition": 6.5, "FrameDurationLimits": (1000000 // 30, 1000000 // 30)})

    timer.set_timer("cooldown", 0.5)

    for i in range(10):
        print(f"Taking pictures in {10 - i} seconds...")
        time.sleep(1)

    counter = 0
    while True:
        frame = camera.capture_array()
        frame = cv2.resize(frame, (camera_x, camera_y))

        results = model.predict(frame, imgsz=128, conf=0.4, workers=4, verbose=False)
        result = results[0].numpy()
        detected_line = result.probs.top1 == 0  # 0 = Line, 1 = Silver

        if ((line and not detected_line) or (silver and detected_line)) and timer.get_timer("cooldown"):
            timer.set_timer("cooldown", 0.5)
            save_image(frame, line)
            counter += 1

        annotated_frame = result.plot()
        cv2.imshow("frame", annotated_frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    print(f"Saved {counter} new images.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--line', action='store_true')
    parser.add_argument('--silver', action='store_true')
    args = parser.parse_args()

    main(args.line, args.silver)
