import requests
from PIL import Image
from pathlib import Path
import os

def fetch_rooftop_image(lat: float, lon: float, api_key: str, output_dir: str) -> tuple:
    """
    Fetch high-res rooftop satellite image from Google Static Maps API
    Returns: (image_path, metadata) or (None, None) if failed
    """
    try:
        # Google Static Maps API URL for satellite imagery
        zoom = 20  # High resolution for rooftops
        size = "640x640"  # Good balance of detail vs speed
        maptype = "satellite"
        
        url = f"https://maps.googleapis.com/maps/api/staticmap?" \
              f"center={lat},{lon}&zoom={zoom}&size={size}&maptype={maptype}&key={api_key}"
        
        print(f"📡 Fetching image from: {url[:80]}...")
        
        # Download image
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        # Save image
        image_path = Path(output_dir) / f"site_{lat:.4f}_{lon:.4f}.jpg"
        with open(image_path, 'wb') as f:
            f.write(response.content)
        
        # Verify it's a valid image
        img = Image.open(image_path)
        img.verify()
        
        # Mock metadata (in real use, parse from API response)
        metadata = {
            "source": "Google Static Maps",
            "zoom": zoom,
            "size_pixels": size,
            "scale_m_per_px": 0.3,  # ~30cm/pixel at zoom 20
            "capture_date": "2025-11-28"  # Would parse from real metadata
        }
        
        print(f"✅ Saved image: {image_path}")
        return str(image_path), metadata
        
    except Exception as e:
        print(f"❌ Image fetch failed: {e}")
        return None, None
