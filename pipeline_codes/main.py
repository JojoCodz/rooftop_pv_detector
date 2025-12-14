import pandas as pd
import os
import json
from pathlib import Path
from pipeline_codes.fetch_image import fetch_rooftop_image
from pipeline_codes.model_inference import run_pv_detection
from pipeline_codes.utils import create_buffer_overlay, compute_qc_status, pixels_to_m2



def main(input_path: str, output_dir: str, model_path: str, api_key: str = None):
    """
    COMPLETE INFERENCE PIPELINE for EcoInnovators Ideathon 2026
    Input: sites.xlsx → Output: JSON + PNG artifacts
    """
    os.makedirs(output_dir, exist_ok=True)
    print(f"Output directory: {output_dir}")

    # 1. READ INPUT .xlsx
    df = pd.read_excel(input_path)
    print(f"Loaded {len(df)} sites to process")
    
    results = []
    
    # 2. PROCESS EACH SITE
    for idx, row in df.iterrows():
        sample_id = row['sample_id']  # ✅ Hackathon format
        lat, lon = row['latitude'], row['longitude']
        output_path = os.path.join(output_dir, f"{sample_id}_rooftop.jpg")
        
        print(f"Processing site {sample_id}: ({lat}, {lon})")
        
        # STEP 1: FETCH ESRI IMAGE
        image_path, metadata = fetch_rooftop_image(
            lat, lon, zoom=17, api_key=api_key, output_path=output_path
        )
        if not image_path:
            print(f"❌ Failed to fetch image for {sample_id}")
            continue
        
        print(f"✅ ESRI image saved: {image_path}")
        
        # STEP 2: RUN YOLO INFERENCE
        detection_results = run_pv_detection(image_path, model_path)
        
        # STEP 3: CREATE BUFFER OVERLAY → CHANGE 1: output_path → output_dir
        buffer_radius_sqft = 1200  # Hackathon requirement
        overlay_path = create_buffer_overlay(
            image_path, lat, lon, buffer_radius_sqft, 
            detection_results, output_dir, sample_id  # ✅ FIXED: output_dir not output_path
        )
        
        # STEP 4: COMPUTE PV AREA (m²)
        pv_area_sqm = 0.0
        bbox_or_mask = "[]"
        if detection_results.get('has_solar', False):
            pv_area_sqm, bbox_or_mask = pixels_to_m2(
                detection_results['masks'], metadata
            )
        
        # STEP 5: QC STATUS → CHANGE 2: Safe access
        qc_status = compute_qc_status(detection_results.get('confidence', 0.0), metadata)
        
        # STEP 6: HACKATHON JSON FORMAT
        result = {
            "sampleid": int(sample_id),  # ✅ Exact hackathon field name
            "lat": float(lat),
            "lon": float(lon),
            "hassolar": detection_results.get('has_solar', False),  # ✅ CHANGE 3: Safe access
            "confidence": float(detection_results.get('confidence', 0.0)),
            "pvareasqmest": round(pv_area_sqm, 2),  # ✅ Hackathon format
            "bufferradiussqft": buffer_radius_sqft,
            "qcstatus": qc_status,  # ✅ Hackathon format
            "bboxormask": bbox_or_mask,
            "imagemetadata": metadata
        }
        results.append(result)
        
        # SAVE PER-SITE JSON ✅
        json_path = os.path.join(output_dir, f"{sample_id}.json")
        with open(json_path, 'w') as f:
            json.dump(result, f, indent=2)
        
        print(f"✅ Site {sample_id} complete: {json_path}")
    
    # SAVE ALL RESULTS ✅
    all_results_path = os.path.join(output_dir, "all_predictions.json")
    with open(all_results_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"✅ Pipeline complete!")
    print(f"📊 Processed {len(results)} sites")
    print(f"📁 Check: {output_dir}/")
    print(f"   - {len([r for r in results if r['hassolar']])} sites WITH solar")
    print(f"   - {len(results) - len([r for r in results if r['hassolar']])} sites NO solar")

if __name__ == "__main__":
    # CONFIG - UPDATE PATHS
    INPUT_XLSX = "inputs/sites.xlsx"  # ✅ In project root
    OUTPUT_DIR = "outputs/"    # ✅ Creates automatically
    MODEL_PATH = "models/best.pt"  # ✅ Your trained YOLO model
    
    main(INPUT_XLSX, OUTPUT_DIR, MODEL_PATH, api_key=None)