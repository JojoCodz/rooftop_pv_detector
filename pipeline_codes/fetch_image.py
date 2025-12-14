import requests
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import os
from io import BytesIO

def fetch_rooftop_image(lat, lon, zoom=19, size=512, api_key=None, output_path=None):
    def latlon_to_tile(lat, lon, zoom):
        n = 2 ** zoom
        lat_rad = np.radians(lat)
        x = int((lon + 180.0) / 360.0 * n)
        y = int((1.0 - np.log(np.tan(lat_rad) + (1 / np.cos(lat_rad))) / np.pi) / 2.0 * n)
        return x, y, zoom
    
    x, y, z = latlon_to_tile(lat, lon, zoom)
    tile_url = f"https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
    
    try:
        response = requests.get(tile_url, timeout=10)
        response.raise_for_status()
        img = Image.open(BytesIO(response.content))
        
        # Add ESRI watermark
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("arial.ttf", 12)
        except:
            font = ImageFont.load_default()
        draw.text((5, 5), "© Esri", fill=(255,255,255), font=font)
        
        img_resized = img.resize((size, size))
        
        # ALWAYS save if output_path provided
        if output_path:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            img_resized.save(output_path)
        
        metadata = {
            "source": "ESRI World Imagery",
            "zoom": z, "tile_coords": (x, y),
            "lat": lat, "lon": lon,
            "img_size": size
        }
        
        # ALWAYS return 2 values: (image_path, metadata)
        return output_path if output_path else None, metadata
        
    except Exception as e:
        print(f"ESRI fetch failed: {e}")
        return None, None  # ← ALWAYS 2 values
