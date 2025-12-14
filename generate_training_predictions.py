from ultralytics import YOLO
from glob import glob
import os
import json

MODEL_PATH = "models/best.pt"
TRAIN_IMAGES_DIR = "data/train7"   # change if your path is different
OUT_JSON = "predictions_training_dataset.json"

def main():
    model = YOLO(MODEL_PATH)
    image_paths = sorted(glob(os.path.join(TRAIN_IMAGES_DIR, "*.jpg")) +
                         glob(os.path.join(TRAIN_IMAGES_DIR, "*.png")))

    results_all = []
    for img_path in image_paths:
        r = model(img_path, verbose=False)[0]
        detections = []
        if r.boxes is not None:
            for box in r.boxes:
                xyxy = box.xyxy[0].tolist()
                conf = float(box.conf[0])
                cls = int(box.cls[0])
                detections.append({
                    "bbox_xyxy": xyxy,
                    "confidence": conf,
                    "class_id": cls
                })

        results_all.append({
            "image": os.path.basename(img_path),
            "detections": detections
        })

    with open(OUT_JSON, "w") as f:
        json.dump(results_all, f, indent=2)

    print(f"Saved training predictions to {OUT_JSON}")
    print(f"Total images: {len(image_paths)}")

if __name__ == "__main__":
    main()
