from ultralytics import YOLO
from glob import glob
import os

MODEL_PATH = "models/best.pt"
TRAIN_IMAGES_DIR = "data/train/images"           # adjust if needed
OUT_DIR = "artefacts/training_images"            # folder required by challenge

def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    model = YOLO(MODEL_PATH)

    image_paths = sorted(glob(os.path.join(TRAIN_IMAGES_DIR, "*.jpg")) +
                         glob(os.path.join(TRAIN_IMAGES_DIR, "*.png")))

    # save=True + project/name lets Ultralytics write overlays for you
    model.predict(
        source=image_paths,
        save=True,
        project=OUT_DIR,
        name="yolo_overlays",
        imgsz=640,
        verbose=False
    )

    print(f"Saved artefacts to {OUT_DIR}/yolo_overlays")

if __name__ == "__main__":
    main()
