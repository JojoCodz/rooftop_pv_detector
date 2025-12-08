from ultralytics import YOLO
from pathlib import Path

# 1) Point to your trained weights
MODEL_PATH = "models/best.pt"

# 2) Point to an image that should contain solar panels
IMAGE_PATH = "buffer/Screenshot 2025-12-04 102637.png"  # change to any PNG/JPG you want

def main():
    model = YOLO(MODEL_PATH)

    # Run inference with a slightly lower conf threshold
    results = model(IMAGE_PATH, conf=0.2, imgsz=512)[0]

    print(f"Detections on {IMAGE_PATH}: {len(results.boxes)} boxes")
    for box in results.boxes:
        x1, y1, x2, y2 = box.xyxy[0].tolist()
        conf = float(box.conf[0])
        cls_id = int(box.cls[0])
        print(f"  bbox={x1:.1f},{y1:.1f},{x2:.1f},{y2:.1f}  conf={conf:.2f}  class={cls_id}")

    # Save an image with boxes drawn so you can see them
    save_path = Path("outputs") / "debug_detection.png"
    save_path.parent.mkdir(parents=True, exist_ok=True)

    # Save overlay image
    results.plot(save=True, filename=str(save_path))
    print(f"Saved debug overlay to {outputs/debug_detection.png}")

if __name__ == "__main__":
    main()
