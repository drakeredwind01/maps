'''
Feature	Raw SanGIS GeoJSON	Your "Slim" GeoJSON
File Size	50MB+ (Slow to load)	2MB (Fast & smooth)
Data	Every detail (Overwhelming)	Just Elevation (Useful)
User Experience	Map "stutters" or crashes	Map feels like Google Maps
'''



import geopandas as gpd
from shapely.geometry import box
import os

# --- CONFIGURATION ---
INPUT_PATH = "/media/drake/A662-9307/python/Topo_40ft_1999_SG.geojson"
OUTPUT_FILE = "ib_to_santee_topo_slim.json"

# 1. Load the file
if not os.path.exists(INPUT_PATH):
    print(f"❌ ERROR: File not found at {INPUT_PATH}")
else:
    print("📂 Loading GeoJSON...")
    topo = gpd.read_file(INPUT_PATH)
    
    # 2. MATCH THE COORDINATES
    # Create our GPS bounding box
    gps_box = box(-117.15, 32.53, -116.90, 32.88)
    # Put that box into a temporary GeoDataFrame so we can translate it
    box_gdf = gpd.GeoDataFrame(geometry=[gps_box], crs="EPSG:4326")
    # Translate the box to match the Topo file's feet (EPSG:2230)
    target_box = box_gdf.to_crs(topo.crs).geometry.iloc[0]

    print("✂️ Clipping to your area (IB to Santee)...")
    topo_slice = topo.clip(target_box)

    print("🧹 Slimming columns and simplifying...")
    # Keep only the elevation column
    if 'ELEV' in topo_slice.columns:
        topo_slice = topo_slice[['ELEV', 'geometry']]
    
    # Simplify the lines (5 foot tolerance is safe for 40ft contours)
    topo_slice['geometry'] = topo_slice.simplify(5.0)

    # 3. CONVERT BACK TO GPS (Required for Web Maps like Leaflet)
    print("🌍 Converting to Web Coordinates (GPS)...")
    topo_slice = topo_slice.to_crs("EPSG:4326")

    print(f"💾 Saving to {OUTPUT_FILE}...")
    topo_slice.to_file(OUTPUT_FILE, driver='GeoJSON')
    
    print(f"✅ Success! Found {len(topo_slice)} contour lines.")