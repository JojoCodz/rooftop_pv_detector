from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional

from PIL import Image, ImageDraw


# ---------- Area conversion ----------

def pixels_to_m2(masks: List[Dict[str, Any]], image_metadata: Dict[str, Any]) -> Tuple[float, str]:
    """
    Convert total PV pixel area to m² and return (area_m2, bbox_or_mask_str).

    masks: list with items like {"bbox": [x1,y1,x2,y2], "pixel_area": ...}
    image_metadata: must contain "meters_per_pixel" (linear resolution in m/px).
    """
    mpp = float(image_metadata.get("meters_per_pixel", 0.3))  # fallback 0.3 m/px
    if mpp <= 0 or not masks:
        return 0.0, "[]"

    total_pixel_area = sum(float(m["pixel_area"]) for m in masks if m.get("pixel_area", 0) > 0)
    area_m2 = total_pixel_area * (mpp ** 2)

    # Encode bboxes as a simple JSON‑serializable string
    bbox_list = [m["bbox"] for m in masks if "bbox" in m]
    return float(area_m2), str(bbox_list)


# ---------- QC status ----------

def compute_qc_status(
    confidence: Optional[float],
    image_metadata: Dict[str, Any],
    min_conf: float = 0.6,
    min_resolution: Tuple[int, int] = (256, 256),
) -> str:
    """
    Decide VERIFIABLE / NOT_VERIFIABLE based on confidence and image quality.
    """
    width = image_metadata.get("width")
    height = image_metadata.get("height")
    cloud_cover = image_metadata.get("cloud_cover", 0.0)  # 0–1
    stale = image_metadata.get("stale", False)

    if width is not None and height is not None:
        if width < min_resolution[0] or height < min_resolution[1]:
            return "NOT_VERIFIABLE"
    if cloud_cover is not None and cloud_cover > 0.5:
        return "NOT_VERIFIABLE"
    if stale:
        return "NOT_VERIFIABLE"

    if confidence is None:
        return "NOT_VERIFIABLE"
    return "VERIFIABLE" if confidence >= min_conf else "NOT_VERIFIABLE"


# ---------- Overlay creation ----------

def create_buffer_overlay(
    image_path: str,
    lat: float,
    lon: float,
    buffer_radius_sqft: float,
    detection_results: Dict[str, Any],
    output_dir: str,
    sample_id: Any,
) -> str:
    """
    Draw a simple audit overlay with detection bboxes and save it.

    NOTE: For now, buffer_radius_sqft is only used for the legend; it is not
    georeferenced. This still produces a useful visual artifact for auditors.
    """
    img = Image.open(image_path).convert("RGB")
    draw = ImageDraw.Draw(img, "RGBA")

    width, height = img.size

    # Draw detections as green boxes
    masks = detection_results.get("masks", [])
    for m in masks:
        if "bbox" not in m:
            continue
        x1, y1, x2, y2 = m["bbox"]
        draw.rectangle([x1, y1, x2, y2], outline=(0, 255, 0, 255), width=3)

    # Optional: write a small legend at the top‑left
    text = f"sample_id={sample_id}, buffer={buffer_radius_sqft} sqft"
    bbox = draw.textbbox((0, 0), text)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.rectangle([0, 0, tw + 4, th + 4], fill=(0, 0, 0, 160))
    draw.text((2, 2), text, fill=(255, 255, 255, 255))

    out_dir = Path(output_dir) / "overlays"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{sample_id}.png"
    img.save(out_path)

    # Also update width/height in metadata if caller wants to use it
    return str(out_path)
