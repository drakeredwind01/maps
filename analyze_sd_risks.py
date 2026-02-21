# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "osmnx>=2.0.0",
#     "geopandas",
#     "matplotlib",
#     "shapely",
#     "pyarrow",
#     "pyogrio",
# ]
# ///

import osmnx as ox
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import box
import warnings
import os
import pandas as pd

# Ignore geometry warnings for a cleaner output
warnings.filterwarnings("ignore")

# 1. Configuration
osm_file = os.path.expanduser("~/Downloads/socal-260220.osm.pbf")

# Narrowing the scope to the "College Area" (Downtown/City College) 
# for much faster extraction and testing.
# [north, south, east, west]
sd_bbox_coords = (32.725, 32.710, -117.140, -117.160)
north, south, east, west = sd_bbox_coords

# Create a shapely box for clipping local data
sd_box = box(west, south, east, north)

print(f"Checking for local file: {osm_file}")
if not os.path.exists(osm_file):
    print(f"CRITICAL ERROR: Local file NOT found at {osm_file}")
    exit()

def load_local_features(layer_name):
    """
    Reads specific layers from the local PBF file using geopandas/pyogrio.
    """
    print(f" - Extracting {layer_name} from local file (College Area Slice)...")
    try:
        gdf = gpd.read_file(
            osm_file, 
            layer=layer_name, 
            bbox=(west, south, east, north),
            engine="pyogrio"
        )
        return gdf
    except Exception as e:
        print(f"Error reading {layer_name}: {e}")
        return gpd.GeoDataFrame()

# 2. Extract Data from Local File
lines_gdf = load_local_features('lines')

# Filter for Freeways (checking both direct columns and 'other_tags' string)
def filter_tags(gdf, key, values):
    if gdf.empty: return gdf
    mask = pd.Series(False, index=gdf.index)
    if key in gdf.columns:
        mask |= gdf[key].isin(values)
    if 'other_tags' in gdf.columns:
        # PBF files often store tags as '"key"=>"value","key2"=>"value2"'
        for val in values:
            mask |= gdf['other_tags'].str.contains(f'"{key}"=>"{val}"', na=False)
    return gdf[mask]

freeways = filter_tags(lines_gdf, 'highway', ['motorway', 'trunk'])
rivers = filter_tags(lines_gdf, 'waterway', ['river', 'stream'])

# Extract Airports from multipolygons layer (Now much faster due to tiny BBOX)
polygons_gdf = load_local_features('multipolygons')
airports = filter_tags(polygons_gdf, 'aeroway', ['aerodrome', 'runway'])

print(f"Found: {len(freeways)} freeway segments, {len(rivers)} river segments, {len(airports)} airport polygons.")

print("Calculating buffers...")

def safe_buffer(gdf, distance_meters):
    if gdf is None or gdf.empty:
        return None
    try:
        # Determine the UTM zone for San Diego (Zone 11N / EPSG:32611)
        gdf_projected = gdf.to_crs(epsg=32611)
        buffer_geom = gdf_projected.buffer(distance_meters)
        return gpd.GeoDataFrame(geometry=buffer_geom, crs=gdf_projected.crs).to_crs(epsg=4326)
    except Exception as e:
        print(f"Skipping buffer: {e}")
        return None

# Buffers: 2000ft (~610m), 5 miles (~8046m), 1000ft (~300m)
freeway_zones = safe_buffer(freeways, 610)
airport_zones = safe_buffer(airports, 8046)
river_zones = safe_buffer(rivers, 300)

print("Visualizing results...")

# 5. Plotting
fig, ax = plt.subplots(figsize=(12, 12))

# Plot the background
gpd.GeoSeries([sd_box]).plot(ax=ax, color='#f8f8f8', edgecolor='black', linewidth=1)

# Plot the river lines
if not rivers.empty:
    rivers.plot(ax=ax, color='blue', alpha=0.3, linewidth=1, label='Waterways')

# Plot the exclusion zones
if airport_zones is not None and not airport_zones.empty:
    airport_zones.plot(ax=ax, color='orange', alpha=0.15, label='Airport Exclusion (5mi)')

if freeway_zones is not None and not freeway_zones.empty:
    freeway_zones.plot(ax=ax, color='red', alpha=0.3, label='Freeway Exclusion (2000ft)')

if river_zones is not None and not river_zones.empty:
    river_zones.plot(ax=ax, color='cyan', alpha=0.4, label='Flood Proxy (1000ft)')

# Force the plot view to our specific college bounding box
ax.set_xlim(west, east)
ax.set_ylim(south, north)

ax.set_title("Test Area: San Diego City College & Surroundings\n(Rapid Extraction Mode)")
ax.set_xlabel("Longitude")
ax.set_ylabel("Latitude")
plt.legend(loc='upper right')
plt.grid(True, linestyle=':', alpha=0.5)

plt.savefig("sd_exclusion_map.png", dpi=300)
print("Success! Map saved as 'sd_exclusion_map.png'.")
plt.show()