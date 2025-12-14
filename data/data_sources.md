# Training Data Sources

The rooftop PV detection model was trained on a combined dataset built from three Roboflow projects, each exported in YOLOv8 format and then merged in Google Colab.

---

## Source 1 – LSGI547 Project

- Platform: Roboflow
- Workspace ID: `projectsolarpanel`
- Project ID (slug): `lsgi547-project`
- Version: `3`
- Export format: `YOLOv8`
- Notes: Contains rooftop imagery with solar panels and negatives from the LSGI547 course project.

How to re-download:

from roboflow import Roboflow
rf = Roboflow(api_key="YOUR_API_KEY")
project = rf.workspace("projectsolarpanel").project("lsgi547-project")
version = project.version(3)
dataset = version.download("yolov8")

---

## Source 2 – Custom Workflow Object Detection

- Platform: Roboflow
- Workspace ID: `alfred-weber-institute-of-economics`
- Project ID (slug): `custom-workflow-object-detection-tgnqc`
- Version: `8`
- Export format: `YOLOv8`
- Notes: Main dataset used in the EcoInnovators challenge brief (“Custom Workflow Object Detection”).

How to re-download:

from roboflow import Roboflow
rf = Roboflow(api_key="YOUR_API_KEY")
project = rf.workspace("alfred-weber-institute-of-economics").project(
"custom-workflow-object-detection-tgnqc"
)
version = project.version(8)
dataset = version.download("yolov8")

---

## Source 3 – Solar Panels (Piscinas y Tenistable)

- Platform: Roboflow
- Workspace ID: `piscinas-y-tenistable`
- Project ID (slug): `solar-panels-ba8ty`
- Version: `1`
- Export format: `YOLOv8`
- Notes: Additional rooftop solar imagery to improve generalization.

How to re-download:

from roboflow import Roboflow
rf = Roboflow(api_key="YOUR_API_KEY")
project = rf.workspace("piscinas-y-tenistable").project("solar-panels-ba8ty")
version = project.version(1)
dataset = version.download("yolov8")

---

## Combined Dataset Construction

1. Each dataset above was downloaded in YOLOv8 format in Google Colab.
2. The `train/`, `valid/`, and `test/` splits from all three projects were merged into a single directory structure:

   - `combined_dataset/train/images`, `combined_dataset/train/labels`  
   - `combined_dataset/valid/images`, `combined_dataset/valid/labels`  
   - `combined_dataset/test/images`, `combined_dataset/test/labels`

3. A single `data/rooftop_pv.yaml` file points to this merged dataset and defines one class:

path: /content/combined_dataset
train: train/images
val: valid/images
test: test/images

nc: 1
names: ["Solarpanel"]

This file documents all training data sources and how to reconstruct the combined dataset used to train `best.pt`.