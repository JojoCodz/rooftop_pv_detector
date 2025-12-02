from ultralytics import YOLO

# 1) Load a small pretrained model
model = YOLO("runs/detect/train5/weights/last.pt")  # or yolov8n.pt you downloaded

# 2) Train on your Roboflow dataset
model.train(
    data="data/custom-workflow-object-detection-tgnqc-8/data.yaml",
    epochs=3,
    imgsz=512,
    batch=2
)