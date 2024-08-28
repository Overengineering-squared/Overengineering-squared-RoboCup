import time

import cv2
from libcamera import controls
from picamera2 import Picamera2


def line_cam_loop():
    camera_x = 448  # 336 448
    camera_y = 252  # 368 336

    camera = Picamera2()
    print(camera.sensor_modes)

    mode = camera.sensor_modes[0]
    print(mode)

    camera.configure(camera.create_video_configuration(sensor={'output_size': mode['size']}))
    camera.start()

    # print(camera.camera_controls)
    camera.set_controls({"AfMode": controls.AfModeEnum.Manual, "LensPosition": 6.5, "FrameDurationLimits": (1000000 // 120, 1000000 // 120)})  # ({"AfMode": controls.AfModeEnum.Manual, "LensPosition": 6.5, "FrameDurationLimits": (1000000 // 60, 1000000 // 60)})  {"AfMode": controls.AfModeEnum.Manual, "LensPosition": 0.4} {"AfMode": controls.AfModeEnum.Continuous, "AfSpeed": controls.AfSpeedEnum.Fast}
    # print(camera.camera_controls)

    print(camera.camera_configuration())
    time.sleep(0.1)

    fps_time = time.perf_counter()
    counter = 0
    fps = 0

    while True:
        rawCapture = camera.capture_array()
        # print(rawCapture.shape)
        # rawCapture = cv2.cvtColor(rawCapture, cv2.COLOR_YUV2BGR_I420)
        rawCapture = cv2.resize(rawCapture, (camera_x, camera_y))

        counter += 1
        if time.perf_counter() - fps_time > 1:
            fps = int(counter / (time.perf_counter() - fps_time))
            fps_time = time.perf_counter()
            counter = 0

        cv2.putText(
                rawCapture, str(fps), (int(camera_x * 0.92), int(camera_y * 0.05)), cv2.FONT_HERSHEY_DUPLEX, 0.5,
                (0, 255, 0), 1
                )

        cv2.imshow("Line Camera2", rawCapture)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


line_cam_loop()
