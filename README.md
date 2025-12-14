This repository implements a complete, auditable pipeline for rooftop solar PV detection for the EcoInnovators Ideathon 2026 challenge. It takes a .xlsx file of sites with latitude/longitude, fetches recent rooftop imagery from ESRI World Imagery, runs a trained YOLO model, and produces JSON outputs and visual artifacts per site.​

Project Structure
text
ROOFTOP_PV_DETECTOR/
├── buffer/
├── data/
│   └── rooftop_pv.yaml          # YOLO dataset config (training)
├── inputs/
│   └── sites.xlsx               # Sample IDs + lat/lon for inference
├── models/
│   └── best.pt                  # Trained YOLO model weights
├── outputs/                     # Auto-generated inference outputs
├── pipeline_codes/
│   ├── main.py                  # MAIN inference pipeline (entry point)
│   ├── fetch_image.py           # Fetch ESRI rooftop imagery
│   ├── model_inference.py       # YOLO inference wrapper
│   └── utils.py                 # Buffers, overlays, QC, area conversion
├── runs/                        # YOLO training runs / logs
├── downloaded_dataset.py        # Helper to download/prepare training data
├── train_yolo.py                # Script to train YOLO on rooftop_pv.yaml
├── test_model.py                # Quick local test on sample image
├── requirements.txt             # Python dependencies
└── README.md                    # This file
1. Environment Setup
1.1. Python version
Recommended: Python 3.10+ (tested with 3.12)

Create and activate a virtual environment (optional but recommended):

bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate
1.2. Install dependencies
bash
pip install -r requirements.txt
This installs ultralytics, torch, pandas, opencv-python, numpy, and other utilities required for the pipeline.​

2. Inputs and Expected Outputs
2.1. Input .xlsx format
Place your input file at:

text
inputs/sites.xlsx
Required columns in sites.xlsx:

sample_id – Unique site ID

latitude – Latitude in WGS84

longitude – Longitude in WGS84

Example row:

sample_id	latitude	longitude
1001	37.4222472	-122.0851754
​

2.2. Output JSON format (per site)
For each site, the pipeline creates a JSON file in outputs/:

json
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
    "tile_coords": [x, y],
    "img_size": 512
  }
}
A combined all_predictions.json is also written to outputs/.​

2.3. Visual artifacts
For each site, the pipeline produces:

outputs/<sample_id>_rooftop.jpg – Fetched ESRI rooftop image (512×512, with attribution)

outputs/overlays/<sample_id>_overlay.png – Overlay of detection(s) + buffer polygon for auditability

3. Running the Inference Pipeline
3.1. Prepare required assets
Ensure inputs/sites.xlsx exists with the expected schema.

Place your trained YOLO weights at:

text
models/best.pt
These weights are typically obtained from train_yolo.py or a Colab run.​

3.2. Run pipeline from project root
From the repository root (ROOFTOP_PV_DETECTOR/), run:

bash
python -m pipeline_codes.main
This uses the default configuration inside pipeline_codes/main.py:

python
INPUT_XLSX = "inputs/sites.xlsx"
OUTPUT_DIR = "outputs/"
MODEL_PATH = "models/best.pt"
main(INPUT_XLSX, OUTPUT_DIR, MODEL_PATH, api_key=None)
What this does for each row in sites.xlsx:

Fetch a high-resolution rooftop image centered at (lat, lon) from ESRI World Imagery using fetch_rooftop_image().

Classify presence/absence of rooftop solar panels via YOLO in run_pv_detection().

Quantify PV area within a 1200 sq ft buffer using pixels_to_m2().

Explain via create_buffer_overlay() (buffer + detections) and compute_qc_status().

Store per-site JSON and overlay artifacts into outputs/.​

4. Training the YOLO Model
4.1. Data config
The YAML config for training lives at:

text
data/rooftop_pv.yaml
It specifies train/val image directories and class definitions (solar_panel).​

4.2. Train script
To train YOLO on the rooftop PV dataset:

bash
python train_yolo.py
A typical train_yolo.py call looks like:

python
from ultralytics import YOLO

model = YOLO("yolov8n.pt")  # or your previous best.pt
model.train(
    data="data/rooftop_pv.yaml",
    epochs=100,
    imgsz=640,
    batch=16,
    device="cpu",      # or "0" if you have a GPU
    save_period=5      # save checkpoints every 5 epochs
)
Training outputs (including best.pt, last.pt, results.csv) will appear under runs/detect/train/.​​

5. Prediction Files, Artifacts, and Logs (Deliverables)
To satisfy the challenge deliverables for the training dataset:​

5.1. Prediction files (training set)
After training, run a script (e.g., test_model.py) to generate training predictions:

bash
python test_model.py
This should:

Load models/best.pt

Iterate over training images

Write a predictions_training_dataset.json file at repo root or outputs/

5.2. Artifacts (training set)
test_model.py (or a similar script) should also save:

Detection overlays for training images into an artefacts/ (or artifacts/) folder:

e.g., artefacts/train/<image_name>_overlay.png

5.3. Training logs
From the YOLO run directory:

Copy runs/detect/train/results.csv to:

text
training_logs.csv
This CSV contains loss, precision, recall, and mAP across epochs, satisfying the log requirement.​​

6. Imagery Sources, Licensing, and Attribution
This project only uses permissible imagery sources for training and inference:​

ESRI World Imagery for inference:

Accessed via the ArcGIS REST World_Imagery tile service in fetch_image.py

Attribution:
Tiles © Esri — Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community

Roboflow public datasets such as:

Alfred Weber Institute of Economics (solar mapping)

LSGI547 Project

Piscinas Y Tenistable
(Exact dataset links and licenses documented in the model card.)

No OpenStreetMap raster tiles are used for inference or training. All usage respects provider terms, and sources are clearly cited in the Model Card and code comments.​

7. Model Card and License
Model Card: model_card.pdf in repo root describes:

Data used, assumptions, logic

Known limitations, biases, and failure modes

Retraining and evaluation guidance
(Format inspired by “Model Cards for Model Reporting” by Mitchell et al.)​

License:

Code: e.g., MIT License (see LICENSE file in repo)

Imagery & datasets: Governed by their respective providers (ESRI, Roboflow datasets); see Model Card for details.​

8. Notes and Limitations
The model may struggle on:

Very low-resolution imagery

Heavy occlusion (trees, tanks) or extreme shadows

Roof types and regions not represented in training data

All high-stakes decisions (e.g., subsidy approvals) should be verified by a human reviewer using the generated overlays and QC status.​

9. Quick Start Checklist
Clone repo and cd into ROOFTOP_PV_DETECTOR/.

Create venv and pip install -r requirements.txt.

Ensure:

inputs/sites.xlsx is present with correct columns.

models/best.pt exists (trained model).

Run:

bash
python -m pipeline_codes.main
Inspect outputs in outputs/ and overlays in outputs/overlays/.
