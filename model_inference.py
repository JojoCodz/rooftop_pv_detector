from typing import Dict, Any
from ultralytics import YOLO


def run_pv_detection(image_path: str, model_path: str) -> Dict[str, Any]:
    """
    Run YOLO detection on a rooftop image and return a compact dict
    that main.py expects.
    """
    model = YOLO(model_path)
    results = model(image_path)[0]  # first image

    has_solar = len(results.boxes) > 0

    # Take max confidence over all detections as site‑level confidence
    if has_solar:
        confs = results.boxes.conf.cpu().tolist()
        site_conf = max(confs)
    else:
        site_conf = 0.0

    # For area we approximate each bbox as a rectangle in pixels
    masks = []
    for box in results.boxes.xyxy.cpu().tolist():
        x1, y1, x2, y2 = box
        pixel_area = (x2 - x1) * (y2 - y1)
        masks.append(
            {
                "bbox": [x1, y1, x2, y2],
                "pixel_area": pixel_area,
            }
        )

    return {
        "has_solar": has_solar,
        "confidence": float(site_conf),
        "masks": masks,  # list of dicts, used by pixels_to_m2 and overlay
        "raw_results": results,  # optional: full YOLO Results object
    }
# ---------- PV area computation ----------