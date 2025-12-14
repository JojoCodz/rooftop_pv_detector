from ultralytics import YOLO
from glob import glob
import os, json

MODEL_PATH = "/content/best.pt"  # or runs/detect/train7/weights/best.pt
TRAIN_IMAGES_DIR = "/content/Custom-Workflow-Object-Detection-8/train/images"  # use the folder that showed 9360 images
OUT_JSON = "/content/predictions_training_dataset.json"

model = YOLO(MODEL_PATH)
image_paths = sorted(glob(os.path.join(TRAIN_IMAGES_DIR, "*.jpg")) +
                     glob(os.path.join(TRAIN_IMAGES_DIR, "*.png")))
print("Images to process:", len(image_paths))

results_all = []
for img_path in image_paths:
    r = model(img_path, verbose=False)[0]
    dets = []
    if r.boxes is not None:
        for box in r.boxes:
            xyxy = box.xyxy[0].tolist()
            conf = float(box.conf[0])
            cls = int(box.cls[0])
            dets.append({
                "bbox_xyxy": xyxy,
                "confidence": conf,
                "class_id": cls
            })
    results_all.append({
        "image": os.path.basename(img_path),
        "detections": dets
    })

with open(OUT_JSON, "w") as f:
    json.dump(results_all, f, indent=2)

print("Saved training predictions to", OUT_JSON)
