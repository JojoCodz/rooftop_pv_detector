import pandas as pd
import os
import json
from pathlib import Path
from fetch_image import fetch_rooftop_image
from model_inference import run_pv_detection
from utils import create_buffer_overlay, compute_qc_status, pixels_to_m2

def main(input_path: str, output_path: str, model_path: str, api_key: str):
    """
    COMPLETE INFERENCE PIPELINE for EcoInnovators Ideathon 2026
    Input: sites.xlsx → Output: JSON + PNG artifacts
    """
    # 1. READ INPUT .xlsx
    df = pd.read_excel(input_path)
    print(f"Loaded {len(df)} sites to process")
    
    os.makedirs(output_path, exist_ok=True)
    
    results = []
    
    # 2. PROCESS EACH SITE
    for idx, row in df.iterrows():
        sample_id = row['sample_id']
        lat, lon = row['latitude'], row['longitude']
        print(f"Processing site {sample_id}: ({lat}, {lon})")
        
        # STEP 1: FETCH IMAGE
        image_path, metadata = fetch_rooftop_image(lat, lon, api_key, output_path)
        if not image_path:
            print(f"❌ Failed to fetch image for {sample_id}")
            continue
            
        # STEP 2: RUN MODEL INFERENCE
        detection_results = run_pv_detection(image_path, model_path)
        
        # STEP 3: CREATE BUFFER OVERLAY
        buffer_radius_sqft = 1200  # Start with small buffer
        overlay_path = create_buffer_overlay(
            image_path, lat, lon, buffer_radius_sqft, detection_results, output_path, sample_id
        )
        
        # STEP 4: COMPUTE PV AREA (m²)
        pv_area_sqm = 0.0
        bbox_or_mask = "[]"
        if detection_results['has_solar']:
            pv_area_sqm, bbox_or_mask = pixels_to_m2(detection_results['masks'], metadata)
        
        # STEP 5: QC STATUS
        qc_status = compute_qc_status(detection_results['confidence'], metadata)
        
        # STEP 6: SAVE JSON OUTPUT (MANDATORY FORMAT)
        result = {
            "sample_id": int(sample_id),
            "lat": float(lat),
            "lon": float(lon),
            "has_solar": detection_results['has_solar'],
            "confidence": float(detection_results['confidence']),
            "pv_area_sqm_est": round(pv_area_sqm, 2),
            "buffer_radius_sqft": buffer_radius_sqft,
            "qc_status": qc_status,
            "bbox_or_mask": bbox_or_mask,
            "image_metadata": metadata
        }
        results.append(result)
        
        # SAVE PER-SITE JSON
        json_path = Path(output_path) / f"{sample_id}.json"
        with open(json_path, 'w') as f:
            json.dump(result, f, indent=2)
    
    # SAVE ALL RESULTS
    all_results_path = Path(output_path) / "all_predictions.json"
    with open(all_results_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"✅ Pipeline complete! Check outputs/ folder")
    print(f"📊 Processed {len(results)} sites")

if __name__ == "__main__":
    # CONFIG - UPDATE THESE
    INPUT_XLSX = "sites.xlsx"
    OUTPUT_DIR = "outputs/"
    MODEL_PATH = "models/best.pt"  # Your trained YOLO model
    
    main(INPUT_XLSX, OUTPUT_DIR, MODEL_PATH, api_key=None)