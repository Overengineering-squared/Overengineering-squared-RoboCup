from ultralytics import YOLO

model = YOLO('../../../Ai/models/ball_zone_s/ball_detect_s.pt', task='detect')

model.predict(source='zone_images/', imgsz=512, save=True, save_txt=True)
