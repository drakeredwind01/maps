import geopandas as gpd
from shapely.geometry import box

# --- CONFIG ---
INPUT_JSON = "ib_to_santee_topo_slim.json"
OUTPUT_ZONES = "sd_safety_zones.json"

def classify_safety(elev):
    # elevation in your file is likely in feet (based on the 40ft dataset)
    if elev < 50:
        return "Severe Risk"
    elif 50 <= elev < 130:
        return "Caution"
    else:
        return "Safe"

if __name__ == "__main__":
    print("Reading topo data...")
    df = gpd.read_file(INPUT_JSON)

    # Ensure we use the correct column name (case-sensitive)
    # Your example showed 'elevation'
    col = 'elevation' if 'elevation' in df.columns else 'ELEV'

    print("Classifying elevation points...")
    df['safety_level'] = df[col].apply(classify_safety)

    # To make this a 'Map of Areas' rather than just 'Lines', 
    # we group the lines by their safety level.
    # Note: For a true 'Area' map, we'd usually use a DEM, but 
    # since we are staying lightweight, we will group these vectors.
    
    zones = df[['safety_level', 'geometry']].dissolve(by='safety_level')

    # Simplify the resulting complex shapes so the web map stays fast
    zones['geometry'] = zones.simplify(0.0001) 

    print(f"Saving safety zones to {OUTPUT_ZONES}...")
    zones.to_file(OUTPUT_ZONES, driver='GeoJSON')
    
    print("\nCalculated Levels:")
    print(zones.drop(columns='geometry'))
    print("\n✅ Done! Use this file for your 'Safety Overlay' checkbox.")