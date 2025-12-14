text
# Rooftop PV Detector – EcoInnovators Ideathon 2026

This repository implements a complete, auditable pipeline for rooftop solar PV detection for the **EcoInnovators Ideathon 2026** challenge. It takes a `.xlsx` file of sites with latitude/longitude, fetches recent rooftop imagery from **ESRI World Imagery**, runs a trained YOLO model, and produces JSON outputs and visual artifacts per site. [file:669]

---

## 1. Project Structure

ROOFTOP_PV_DETECTOR/
├── buffer/
├── data/
│ └── rooftop_pv.yaml # YOLO dataset config (training)
├── inputs/
│ └── sites.xlsx # Sample IDs + lat/lon for inference
├── models/
│ └── best.pt # Trained YOLO model weights
├── outputs/ # Auto-generated inference outputs
├── pipeline_codes/
│ ├── main.py # MAIN inference pipeline (entry point)
│ ├── fetch_image.py # Fetch ESRI rooftop imagery
│ ├── model_inference.py # YOLO inference wrapper
│ └── utils.py # Buffers, overlays, QC, area conversion
├── runs/ # YOLO training runs / logs
├── downloaded_dataset.py # Helper to download/prepare training data
├── train_yolo.py # Script to train YOLO on rooftop_pv.yaml
├── test_model.py # Quick local test on sample image
├── requirements.txt # Python dependencies
└── README.md # This file

text

---

## 2. Environment Setup

### 2.1 Python version

Recommended: **Python 3.10+** (tested with 3.12).  

Create and activate a virtual environment:

python -m venv .venv

Windows
.venv\Scripts\activate

Linux/Mac
source .venv/bin/activate

text

### 2.2 Install dependencies

pip install -r requirements.txt

text

This installs `ultralytics`, `torch`, `pandas`, `opencv-python`, `numpy`, and other utilities required for the pipeline. [file:669]

---

## 3. Inputs and Expected Outputs

### 3.1 Input `.xlsx` format

Place your input file at:

inputs/sites.xlsx

text

Required columns in `sites.xlsx`:

- `sample_id` – Unique site ID  
- `latitude` – Latitude in WGS84  
- `longitude` – Longitude in WGS84  

Example row:

sample_id,latitude,longitude
1001,37.4222472,-122.0851754

text

[file:669]

### 3.2 Output JSON format (per site)

For each site, the pipeline creates a JSON file in `outputs/`:

{
"sampleid": 1001,
"lat": 37.4222472,
"lon": -122.0851754,
"hassolar": true,
"confidence": 0.92,
"pvareasqmest": 23.5,
"bufferradiussqft": 1200,
"qcstatus": "VERIFIABLE",
"bboxormask": "<encoded polygon or bbox>",
"imagemetadata": {
"source": "ESRI World Imagery",
"zoom": 19,
"tile_coords": ,
"img_size": 512
}
}

text

A combined `all_predictions.json` is also written to `outputs/`. [file:669]

### 3.3 Visual artifacts

For each site, the pipeline produces:

- `outputs/<sample_id>_rooftop.jpg` – Fetched ESRI rooftop image (512×512, with attribution)  
- `outputs/overlays/<sample_id>_overlay.png` – Overlay of detection(s) + buffer polygon for auditability  

---

## 4. Running the Inference Pipeline

### 4.1 Prepare required assets

1. Ensure `inputs/sites.xlsx` exists with the expected schema.  
2. Place your **trained YOLO weights** at:

models/best.pt

text

These weights are typically obtained from `train_yolo.py` or a Colab run. [file:669]

### 4.2 Run pipeline from project root

From the repository root (`ROOFTOP_PV_DETECTOR/`), run:

python -m pipeline_codes.main

text

By default, `pipeline_codes/main.py` uses:

INPUT_XLSX = "inputs/sites.xlsx"
OUTPUT_DIR = "outputs/"
MODEL_PATH = "models/best.pt"

main(INPUT_XLSX, OUTPUT_DIR, MODEL_PATH, api_key=None)

text

For each row in `sites.xlsx`, this will:

1. **Fetch** a high‑resolution rooftop image centered at `(lat, lon)` from **ESRI World Imagery** using `fetch_rooftop_image()`.  
2. **Classify** presence/absence of rooftop solar panels via YOLO in `run_pv_detection()`.  
3. **Quantify** PV area within a 1200 sq ft buffer using `pixels_to_m2()`.  
4. **Explain** via `create_buffer_overlay()` (buffer + detections) and `compute_qc_status()`.  
5. **Store** per-site JSON and overlay artifacts into `outputs/`. [file:669]

---

## 5. Training the YOLO Model

### 5.1 Data config

The YAML config for training lives at:

data/rooftop_pv.yaml

text

It specifies train/val image directories and class definitions (`solar_panel`). [file:669]

### 5.2 Train script

To train YOLO on the rooftop PV dataset:

python train_yolo.py

text

A typical `train_yolo.py` contents:

from ultralytics import YOLO

model = YOLO("yolov8n.pt") # or your previous best.pt
model.train(
data="data/rooftop_pv.yaml",
epochs=100,
imgsz=640,
batch=16,
device="cpu", # or "0" if you have a GPU
save_period=5 # save checkpoints every 5 epochs
)

text

Training outputs (including `best.pt`, `last.pt`, `results.csv`) will appear under:

runs/detect/train/

text

[web:558][file:669]

---

## 6. Prediction Files, Artifacts, and Logs (Training Dataset)

To satisfy the challenge deliverables for the **training dataset**: [file:669]

### 6.1 Prediction files (training set)

After training, generate predictions for all training images (e.g. via `test_model.py`) so that:

predictions_training_dataset.json

text

is created at the repo root or in `outputs/`, containing model outputs for each training image.

### 6.2 Artifacts (training set)

`test_model.py` (or a dedicated script) should:

- Load `models/best.pt`  
- Run inference on all training images  
- Save detection overlays into an `artefacts/` (or `artifacts/`) folder, for example:

artefacts/train/<image_name>_overlay.png

text

### 6.3 Training logs

From the YOLO run directory, copy:

runs/detect/train/results.csv

text

to:

training_logs.csv

text

This CSV contains loss, precision, recall, and mAP across epochs, satisfying the model‑training‑logs requirement. [web:558][file:669]

---

## 7. Imagery Sources, Licensing, and Attribution

This project **only uses permissible imagery sources** for training and inference: [file:669]

- **ESRI World Imagery** (inference):
  - Accessed via the ArcGIS REST `World_Imagery` tile service in `fetch_image.py`.  
  - Attribution (embedded in images and documentation):  
    `Tiles © Esri — Source: Esri, i‑cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR‑EGP, and the GIS User Community.`  
- **Roboflow public datasets** (training):
  - Alfred Weber Institute of Economics (solar mapping)  
  - LSGI547 Project  
  - Piscinas Y Tenistable  
  - Exact dataset links and licenses are documented in the Model Card.

No OpenStreetMap raster tiles are used for inference or training. All usage respects provider terms, and sources are clearly cited in the **Model Card** and within code comments. [file:669]

---

## 8. Model Card and License

- **Model Card**: `model_card.pdf` in the repo root describes:
  - Data used, assumptions, and logic  
  - Known limitations, biases, and failure modes  
  - Retraining and evaluation guidance  
  Inspired by *“Model Cards for Model Reporting”* (Mitchell et al.). [attached_file:1]

- **License**:
  - Code: e.g. **MIT License** (see `LICENSE` file).  
  - Imagery & datasets: Governed by ESRI and individual Roboflow dataset licenses; see the Model Card for details. [file:669]

---

## 9. Notes and Limitations

- The model may struggle on:
  - Very low‑resolution imagery  
  - Heavy occlusion (trees, tanks) or extreme shadows  
  - Roof types and regions not represented in training data  

All high‑stakes decisions (e.g., subsidy approvals) should be verified by a human reviewer using the generated overlays and QC status. [file:669]

---

## 10. Quick Start Checklist

1. Clone the repo and `cd` into `ROOFTOP_PV_DETECTOR/`.  
2. Create a venv and install requirements:

python -m venv .venv
.venv\Scripts\activate # Windows
pip install -r requirements.txt

text

3. Ensure:
- `inputs/sites.xlsx` is present with correct columns.  
- `models/best.pt` exists (trained model).  

4. Run the inference pipeline:

python -m pipeline_codes.main

text

5. Inspect outputs in `outputs/` and overlays in `outputs/overlays/`.
