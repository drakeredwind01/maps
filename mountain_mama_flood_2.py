# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "geopandas",
#     "matplotlib",
#     "shapely",
#     "pyogrio",
#     "contextily",
# ]
# ///
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import contextily as ctx
from shapely.ops import unary_union
import os

# ── settings ────────────────────────────────────────────────────────────────
PBF = "/home/drake/Downloads/socal-260220.osm.pbf"
BBOX = (-117.20, 32.70, -117.10, 32.80) 

# ── 1. Load Waterways from your existing PBF ────────────────────────────────
print("Extracting waterways from PBF...")
rivers = gpd.read_file(PBF, layer="lines", bbox=BBOX, engine="pyogrio")
rivers = rivers[rivers["waterway"].isin(["river", "stream", "canal", "drain", "ditch"])]
print(f"  Found {len(rivers)} water features.")

# ── 2. Create Risk Zones (Buffering) ────────────────────────────────────────
# Convert to a meter-based projection for accurate buffering (UTM 11N)
rivers_proj = rivers.to_crs("EPSG:32611")

print("Calculating flood zones...")
zone_high = rivers_proj.buffer(50)   # 50m: High Risk
zone_med  = rivers_proj.buffer(200)  # 200m: Moderate Risk

# Convert back to Web Mercator for the map
zone_high_gdf = gpd.GeoDataFrame(geometry=[unary_union(zone_high)], crs="EPSG:32611").to_crs("EPSG:3857")
zone_med_gdf  = gpd.GeoDataFrame(geometry=[unary_union(zone_med)], crs="EPSG:32611").to_crs("EPSG:3857")

# ── 3. Plotting ─────────────────────────────────────────────────────────────
print("Rendering map...")
fig, ax = plt.subplots(figsize=(12, 12))

# Plot Moderate Risk (Light Blue)
zone_med_gdf.plot(ax=ax, color="cyan", alpha=0.3, label="Moderate Flood Risk")
# Plot High Risk (Dark Blue)
zone_high_gdf.plot(ax=ax, color="blue", alpha=0.5, label="Flash Flood Zone")

# Add the basemap (Streams from internet, no disk space used)
ctx.add_basemap(ax, source=ctx.providers.OpenStreetMap.Mapnik)

ax.set_axis_off()
ax.set_title("San Diego Hydrological Risk (PBF-Only Version)", fontsize=15)

# Legend
ax.legend(handles=[
    mpatches.Patch(color="blue", alpha=0.5, label="High Risk (50m from Waterway)"),
    mpatches.Patch(color="cyan", alpha=0.3, label="Caution (200m from Waterway)")
], loc='lower right')

plt.savefig("hydro_flood_map.png", dpi=150)
print("Done! Check hydro_flood_map.png")
plt.show()