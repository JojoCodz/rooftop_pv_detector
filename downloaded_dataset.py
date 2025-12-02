# download_dataset.py

import subprocess
import sys

# 1) Install roboflow (run once)
subprocess.check_call([sys.executable, "-m", "pip", "install", "roboflow"])

# 2) Use your real Roboflow API key here (from your Roboflow account)
from roboflow import Roboflow
rf = Roboflow(api_key="YOUR_REAL_API_KEY_HERE")

project = rf.workspace("alfred-weber-institute-of-economics").project("custom-workflow-object-detection-tgnqc")
version = project.version(8)
dataset = version.download("yolov8")   # This creates a folder with data.yaml inside

print("✅ Dataset downloaded:", dataset.location)