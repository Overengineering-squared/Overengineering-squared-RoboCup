import time

import cv2
from picamera2 import Picamera2
from ultralytics import YOLO
from ultralytics.utils.plotting import colors


def main():
    # model = YOLO('../../Ai/models/ball_zone_s/ball_detect_s_edgetpu.tflite', task='detect')  # old model
    model = YOLO('../../Ai/models/ball_zone_s/ball_detect_s_edgetpu.tflite', task='detect')

    camera_height = 480

    crop_percentage = 0.45
    crop_height = int(camera_height * crop_percentage)

    camera = Picamera2(1)
    camera.start()

    fps_time = time.perf_counter()
    counter = 0
    fps = 0

    while True:
        raw_capture = camera.capture_array()
        raw_capture = raw_capture[crop_height:, :]

        cv2_img = cv2.cvtColor(raw_capture, cv2.COLOR_RGBA2BGR)

        results = model.predict(raw_capture, imgsz=(512, 224), conf=0.3, iou=0.2, agnostic_nms=True, workers=4, verbose=False)  # verbose=True to enable debug info

        result = results[0].numpy()

        for box in result.boxes:
            x1, y1, x2, y2 = box.xyxy[0].astype(int)
            class_id = box.cls[0].astype(int)
            name = result.names[class_id]
            confidence = box.conf[0].astype(float)

            color = colors(class_id, True)
            cv2.rectangle(cv2_img, (x1, y1), (x2, y2), color, 2)
            cv2.putText(cv2_img, f"{name}: {confidence:.2f}", (x1, y1 - 5), cv2.FONT_HERSHEY_DUPLEX, 0.5, color, 1, cv2.LINE_AA)

        counter += 1
        if time.perf_counter() - fps_time > 1:
            fps = int(counter / (time.perf_counter() - fps_time))
            fps_time = time.perf_counter()
            counter = 0

        cv2.putText(cv2_img, str(fps), (20, 20), cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 255, 0), 1, cv2.LINE_AA)

        cv2.imshow("YOLOv8 Inference", cv2_img)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
