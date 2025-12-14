from ultralytics import YOLO
from glob import glob
import os

MODEL_PATH = "/content/best.pt"
TRAIN_IMAGES_DIR = "/content/Custom-Workflow-Object-Detection-8/train/images"  # your path
OUT_DIR = "/content/artefacts/training_images"

os.makedirs(OUT_DIR, exist_ok=True)

model = YOLO(MODEL_PATH)
image_paths = sorted(glob(os.path.join(TRAIN_IMAGES_DIR, "*.jpg")) +
                     glob(os.path.join(TRAIN_IMAGES_DIR, "*.png")))
print("Total images:", len(image_paths))

batch_size = 200  # reduce if it still crashes

for i in range(0, len(image_paths), batch_size):
    batch = image_paths[i:i+batch_size]
    print(f"Processing images {i} to {i+len(batch)-1}")
    model.predict(
        source=batch,
        save=True,
        project=OUT_DIR,
        name="yolo_overlays",
        imgsz=640,
        verbose=False
    )
